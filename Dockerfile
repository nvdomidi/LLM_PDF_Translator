FROM ghcr.io/astral-sh/uv:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "st.py"]
