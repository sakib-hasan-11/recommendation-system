import logging

import httpx
import streamlit as st

logger = logging.getLogger(__name__)


def get_api_endpoint() -> str:
    """Get API endpoint from config."""
    import os

    return os.getenv("API_ENDPOINT", "http://localhost:8000")


@st.cache_resource
def get_http_client() -> httpx.AsyncClient:
    """Get HTTP client."""
    return httpx.AsyncClient()


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Movie Recommendations",
        page_icon="🎬",
        layout="wide",
    )

    st.title("🎬 Movie Recommendation System")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        mode = st.radio("Select Mode", ["Get Recommendations", "Find Similar Movies"])

    # Main content
    if mode == "Get Recommendations":
        st.subheader("Get Personalized Recommendations")

        col1, col2 = st.columns([3, 1])

        with col1:
            user_id = st.number_input("Enter User ID", min_value=1, max_value=6040)
        with col2:
            k = st.slider("Number of Recommendations", 5, 50, 10)

        if st.button("Get Recommendations", key="recommend_btn"):
            with st.spinner("Fetching recommendations..."):
                try:
                    api_endpoint = get_api_endpoint()
                    response = httpx.post(
                        f"{api_endpoint}/api/recommend",
                        json={"user_id": int(user_id), "k": k},
                        timeout=30.0,
                    )
                    response.raise_for_status()

                    data = response.json()
                    recommendations = data.get("recommendations", [])

                    if recommendations:
                        st.success(f"Found {len(recommendations)} recommendations!")

                        for idx, rec in enumerate(recommendations, 1):
                            col1, col2, col3 = st.columns([1, 3, 1])
                            with col1:
                                st.metric("Rank", idx)
                            with col2:
                                st.write(f"**{rec.get('name', 'Unknown')}**")
                            with col3:
                                st.metric("Score", f"{rec.get('score', 0):.2f}")
                    else:
                        st.warning("No recommendations found.")

                except httpx.HTTPError as e:
                    st.error(f"API Error: {e}")
                except Exception as e:
                    st.error(f"Error: {e}")

    else:  # Find Similar Movies
        st.subheader("Find Similar Movies")

        col1, col2 = st.columns([3, 1])

        with col1:
            item_id = st.number_input("Enter Movie ID", min_value=1)
        with col2:
            k = st.slider("Number of Similar Movies", 5, 50, 10)

        if st.button("Find Similar", key="similar_btn"):
            with st.spinner("Finding similar movies..."):
                try:
                    api_endpoint = get_api_endpoint()
                    response = httpx.get(
                        f"{api_endpoint}/api/similar/{int(item_id)}",
                        params={"k": k},
                        timeout=30.0,
                    )
                    response.raise_for_status()

                    data = response.json()
                    similar_items = data.get("similar_items", [])

                    if similar_items:
                        st.success(f"Found {len(similar_items)} similar movies!")

                        for idx, item in enumerate(similar_items, 1):
                            col1, col2, col3 = st.columns([1, 3, 1])
                            with col1:
                                st.metric("Rank", idx)
                            with col2:
                                st.write(f"**{item.get('name', 'Unknown')}**")
                            with col3:
                                st.metric("Score", f"{item.get('score', 0):.2f}")
                    else:
                        st.warning("No similar movies found.")

                except httpx.HTTPError as e:
                    st.error(f"API Error: {e}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Footer
    st.divider()
    st.caption("Movie Recommendation System v1.0.0")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
