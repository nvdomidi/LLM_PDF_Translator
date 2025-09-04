import streamlit as st


def apply_custom_styles():
    """Apply clean, modern, minimal CSS styles to the Streamlit app."""
    st.markdown(
        """
    <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global styles */
        .stApp {
            background-color: #fafafa;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Main container */
        .main .block-container {
            max-width: 700px;
            padding: 3rem 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            margin-top: 2rem;
        }
        
        /* Header styling */
        h1 {
            color: #111827 !important;
            font-weight: 600 !important;
            font-size: 2.25rem !important;
            text-align: center;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.025em;
        }
        
        /* Subtitle styling */
        .stCaption > div {
            text-align: center;
            font-size: 1rem !important;
            color: #6b7280 !important;
            margin-bottom: 3rem !important;
            font-weight: 400;
        }
        
        /* File uploader */
        .stFileUploader {
            background: #f9fafb;
            border: 2px dashed #d1d5db;
            border-radius: 8px;
            padding: 2rem 1rem;
            text-align: center;
            margin-bottom: 2rem;
            transition: all 0.2s ease;
        }
        
        .stFileUploader:hover {
            border-color: #9ca3af;
            background: #f3f4f6;
        }
        
        .stFileUploader > div > div > div {
            font-weight: 500;
            color: #374151;
        }
        
        .stFileUploader > div > div > small {
            color: #6b7280;
        }
        
        /* Form inputs - cleaner look */
        .stSelectbox > div > div,
        .stNumberInput > div > div {
            background: white !important;
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        
        .stSelectbox > div > div:focus-within,
        .stNumberInput > div > div:focus-within {
            border-color: #4f46e5 !important;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
        }
        
        /* Labels */
        .stSelectbox > label,
        .stNumberInput > label {
            font-weight: 500 !important;
            color: #374151 !important;
            font-size: 0.9rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Button styling - clean and modern */
        .stButton > button {
            background: #4f46e5 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            width: 100% !important;
            margin-top: 1.5rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stButton > button:hover {
            background: #4338ca !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
        }
        
        .stButton > button:active {
            transform: translateY(1px) !important;
        }
        
        /* Alert messages - subtle and clean */
        .stAlert {
            border: none !important;
            border-radius: 6px !important;
            border-left: 4px solid !important;
            margin: 1rem 0 !important;
            font-size: 0.9rem;
            font-weight: 400;
        }
        
        .stSuccess {
            background: #f0fdf4 !important;
            color: #166534 !important;
            border-left-color: #22c55e !important;
        }
        
        .stError {
            background: #fef2f2 !important;
            color: #dc2626 !important;
            border-left-color: #ef4444 !important;
        }
        
        .stWarning {
            background: #fffbeb !important;
            color: #d97706 !important;
            border-left-color: #f59e0b !important;
        }
        
        .stInfo {
            background: #f0f9ff !important;
            color: #0369a1 !important;
            border-left-color: #3b82f6 !important;
        }
        
        /* Progress bar */
        .stProgress .st-bo {
            background-color: #4f46e5 !important;
        }
        
        /* Metrics styling */
        .stMetric {
            background: #f9fafb !important;
            padding: 1rem !important;
            border-radius: 6px !important;
            border: 1px solid #e5e7eb !important;
        }
        
        .stMetric > div {
            color: #374151 !important;
        }
        
        .stMetric > div > div {
            color: #111827 !important;
            font-weight: 600 !important;
        }
        
        /* Column spacing */
        .row-widget.stHorizontal > div {
            padding: 0 0.5rem;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-color: #e5e7eb !important;
            border-top-color: #4f46e5 !important;
        }
        
        /* Markdown content */
        .stMarkdown h3 {
            color: #111827;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        .stMarkdown p {
            color: #6b7280;
            line-height: 1.6;
        }
        
        .stMarkdown ul {
            color: #6b7280;
        }
        
        .stMarkdown strong {
            color: #374151;
            font-weight: 600;
        }
        
        /* Remove Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 2rem 1rem;
                margin: 1rem;
                border-radius: 8px;
            }
            
            h1 {
                font-size: 1.875rem !important;
            }
            
            .row-widget.stHorizontal > div {
                padding: 0 0.25rem;
            }
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
