import asyncio
import os
import time
from datetime import datetime

import httpx
import streamlit as st

# Environment variables for configuration
API_BASE_URL = os.getenv(
    "API_BASE_URL", "http://backend:8000"
)  # Use Docker Compose service name for backend
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Allow user to override API_BASE_URL from the sidebar in debug mode
if DEBUG:
    import streamlit as st

    st.sidebar.markdown("---")
    API_BASE_URL = st.sidebar.text_input(
        "🔗 API Base URL (override)",
        value=API_BASE_URL,
        help="Set the backend API URL for local or Docker Compose testing.",
    )

# Page configuration
st.set_page_config(
    page_title="AI HR System Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .status-healthy {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    .status-unhealthy {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.title("🔧 Configuration")
    st.write(f"**Environment:** {ENVIRONMENT}")
    st.write(f"**API Base URL:** {API_BASE_URL}")
    st.write(f"**Debug Mode:** {DEBUG}")

    st.markdown("---")
    st.markdown("### Quick Actions")
    if st.button("🔄 Refresh Status"):
        st.rerun()

    st.markdown("---")
    st.markdown("### API Documentation")
    st.markdown(
        f"- **Internal (Docker):** [`{API_BASE_URL}/docs`]({API_BASE_URL}/docs)"
    )
    st.markdown(
        f"- **External (host):** [`http://localhost:8000/docs`](http://localhost:8000/docs)"
    )
    st.info(
        "Use the 'External (host)' link in your browser. The 'Internal (Docker)' link is for container-to-container communication."
    )

# Main content
st.markdown(
    '<h1 class="main-header">🏢 AI HR System Dashboard</h1>', unsafe_allow_html=True
)

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔍 API Health Monitor", "ℹ️ About"])

with tab1:
    st.header("System Overview")

    # API Status Check
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.spinner("Checking API status..."):
            try:
                response = httpx.get(f"{API_BASE_URL}/api/v1/health", timeout=5.0)
                if response.status_code == 200:
                    health_data = response.json()
                    st.success("✅ API Status: Backend API is healthy and responding")

                    # Display metrics
                    with st.container():
                        st.metric(
                            "Response Time", f"{response.elapsed.total_seconds():.3f}s"
                        )
                        st.metric("Status", health_data.get("status", "unknown"))
                        st.metric(
                            "Environment", health_data.get("environment", "unknown")
                        )
                else:
                    st.error("❌ API Status: Backend API is not responding properly")
            except Exception as e:
                st.error("❌ API Status: Cannot connect to backend API")
                if DEBUG:
                    st.error(f"Error: {str(e)}")

    with col2:
        st.info(
            """
**🚀 System**

AI HR System v1.0.0
FastAPI + Streamlit
"""
        )

    with col3:
        st.info(
            """
**🔧 Environment**

Development Mode
Docker Ready
"""
        )

with tab2:
    st.header("API Health Monitor")

    # Manual health check
    if st.button("🔍 Run Health Check"):
        with st.spinner("Performing health check..."):
            start_time = time.time()
            try:
                response = httpx.get(f"{API_BASE_URL}/api/v1/health", timeout=10.0)
                end_time = time.time()

                if response.status_code == 200:
                    health_data = response.json()

                    st.success("✅ Health check passed!")

                    # Display detailed health information
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("System Information")
                        st.write(f"**Status:** {health_data.get('status', 'unknown')}")
                        st.write(
                            f"**Version:** {health_data.get('version', 'unknown')}"
                        )
                        st.write(
                            f"**Environment:** {health_data.get('environment', 'unknown')}"
                        )
                        st.write(f"**Response Time:** {(end_time - start_time):.3f}s")

                    with col2:
                        st.subheader("Timestamp")
                        timestamp = health_data.get("timestamp", datetime.utcnow())
                        if isinstance(timestamp, str):
                            st.write(f"**Last Check:** {timestamp}")
                        else:
                            st.write(f"**Last Check:** {timestamp.isoformat()}")

                    # Raw response
                    with st.expander("📋 Raw Response"):
                        st.json(health_data)

                else:
                    st.error(
                        f"❌ Health check failed with status code: {response.status_code}"
                    )

            except Exception as e:
                st.error(f"❌ Health check failed: {str(e)}")
                if DEBUG:
                    st.exception(e)

with tab3:
    st.header("About AI HR System")

    st.markdown(
        """
    ### 🎯 Project Overview

    This is a simplified scaffold for an AI-powered Human Resources system designed for hackathon development.

    ### 🛠️ Tech Stack

    - **Backend**: FastAPI (Python 3.11)
    - **Frontend**: Streamlit
    - **Package Manager**: uv
    - **Containerization**: Docker & Docker Compose
    - **Environment Management**: python-dotenv + pydantic

    ### 🚀 Features

    - **Health Monitoring**: Real-time API status checks
    - **Environment Configuration**: Flexible settings management
    - **Docker Ready**: Production-ready containerization
    - **CI/CD Ready**: GitHub Actions integration

    ### 🔧 Development

    This scaffold is ready for extension with:
    - User Management & Authentication
    - HR Process Automation
    - AI/ML Integration
    - Database Models
    - Additional API Endpoints

    ### 📚 Next Steps

    1. Add database models and migrations
    2. Implement user authentication
    3. Create HR-specific endpoints
    4. Integrate AI/ML services
    5. Add comprehensive testing
    """
    )

# Footer
st.markdown("---")
st.markdown(
    f"<p style='text-align: center; color: #666;'>AI HR System v1.0.0 | Environment: {ENVIRONMENT} | API: {API_BASE_URL}</p>",
    unsafe_allow_html=True,
)
