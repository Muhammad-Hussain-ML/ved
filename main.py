import streamlit as st
import time
import os
from google import genai
from google.genai import types
import tempfile
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Veo 3 Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 Veo 3 Video Generator")
st.markdown("Generate high-quality 8-second videos with AI using Google's Veo 3 model")

# Sidebar for API configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Google AI API Key", 
        type="password", 
        help="Enter your Google AI API key",
        placeholder="AIz..."
    )
    
    if api_key:
        st.success("✅ API Key configured")
    else:
        st.warning("⚠️ Please enter your API key")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Video Generation")
    
    # Prompt input
    prompt = st.text_area(
        "Video Prompt",
        height=100,
        placeholder="Describe your video... e.g., 'A close-up shot of a tea drop falling into a steaming cup of tea, slow motion, warm lighting'",
        help="Be descriptive! Include details about camera angles, lighting, actions, and style."
    )
    
    # Advanced options
    with st.expander("🎛️ Advanced Options"):
        negative_prompt = st.text_input(
            "Negative Prompt (Optional)",
            placeholder="Things to avoid... e.g., 'blurry, low quality, cartoon'",
            help="Describe what you don't want in the video"
        )
        
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            ["16:9", "9:16"],
            help="Choose video aspect ratio"
        )
        
        person_generation = st.selectbox(
            "Person Generation",
            ["allow_all", "allow_adult", "dont_allow"],
            help="Control generation of people in videos"
        )
    
    # Generate button
    generate_btn = st.button(
        "🎬 Generate Video", 
        type="primary", 
        disabled=not (api_key and prompt),
        use_container_width=True
    )

with col2:
    st.header("🎥 Generated Video")
    
    # Initialize session state
    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
    if 'generating' not in st.session_state:
        st.session_state.generating = False
    if 'operation_id' not in st.session_state:
        st.session_state.operation_id = None

# Video generation logic - Using your exact working code
if generate_btn and api_key and prompt:
    st.session_state.generating = True
    
    try:
        # Configure with your API key - exactly as your working code
        client = genai.Client(api_key=api_key)
        
        # Prepare config for advanced options
        config_params = {}
        if negative_prompt:
            config_params['negative_prompt'] = negative_prompt
        if aspect_ratio:
            config_params['aspect_ratio'] = aspect_ratio
        if person_generation:
            config_params['person_generation'] = person_generation
            
        config = types.GenerateVideosConfig(**config_params) if config_params else None
        
        with st.spinner("🚀 Starting video generation..."):
            # Start video generation - exactly as your working code
            if config:
                operation = client.models.generate_videos(
                    model="veo-3.0-generate-preview",
                    prompt=prompt,
                    config=config
                )
            else:
                operation = client.models.generate_videos(
                    model="veo-3.0-generate-preview",
                    prompt=prompt,
                )
            
            st.session_state.operation_id = operation.name
            st.success(f"✅ Video generation started! Operation ID: {operation.name}")
        
        # Progress tracking with your polling logic
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_elapsed = st.empty()
        
        start_time = time.time()
        
        # Poll the operation status until the video is ready - exactly as your working code
        while not operation.done:
            elapsed = int(time.time() - start_time)
            time_elapsed.text(f"⏱️ Time elapsed: {elapsed} seconds")
            
            # Update progress (estimated)
            if elapsed < 60:
                progress = min(elapsed / 60, 0.9)  # Max 90% until actually done
            else:
                progress = 0.9
            
            progress_bar.progress(progress)
            status_text.info("🎬 Generating your video... This may take 1-6 minutes depending on server load.")
            
            # Wait exactly as your working code
            time.sleep(10)
            operation = client.operations.get(operation)
        
        # Complete progress
        progress_bar.progress(1.0)
        elapsed = int(time.time() - start_time)
        time_elapsed.text(f"✅ Generation completed in {elapsed} seconds!")
        status_text.success("🎉 Video generation completed!")
        
        # Download and save video - exactly as your working code
        with st.spinner("📥 Downloading video..."):
            generated_video = operation.response.generated_videos[0]
            client.files.download(file=generated_video.video)
            
            # Create file in temp directory for Streamlit
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.gettempdir()
            video_filename = f"veo3_video_{timestamp}.mp4"
            video_path = os.path.join(temp_dir, video_filename)
            
            # Save exactly as your working code
            generated_video.video.save(video_path)
            
            st.session_state.video_path = video_path
            st.session_state.generating = False
            
        st.success("🎉 Video ready for viewing and download!")
        st.rerun()
        
    except Exception as e:
        st.session_state.generating = False
        st.error(f"❌ Error generating video: {str(e)}")
        st.error("Please check your API key and try again.")

# Display video if available
if st.session_state.video_path and os.path.exists(st.session_state.video_path):
    with col2:
        st.success("🎉 Your video is ready!")
        
        # Display video
        with open(st.session_state.video_path, 'rb') as video_file:
            video_bytes = video_file.read()
            st.video(video_bytes)
        
        # Video info
        file_size = os.path.getsize(st.session_state.video_path) / (1024 * 1024)  # MB
        st.info(f"📊 Video Info: 720p, 8 seconds, {file_size:.2f} MB")
        
        # Download button
        with open(st.session_state.video_path, 'rb') as video_file:
            st.download_button(
                label="⬇️ Download Video",
                data=video_file.read(),
                file_name=f"veo3_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                mime="video/mp4",
                type="primary",
                use_container_width=True
            )

# Show generation status
if st.session_state.generating:
    with col2:
        st.info("🎬 Video is being generated... Please wait.")

# Footer with tips
st.markdown("---")
st.markdown("### 💡 Pro Tips for Better Videos")

tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    **🎯 Prompt Writing Tips:**
    - Be specific about camera angles (close-up, wide shot, etc.)
    - Include lighting details (natural light, golden hour, etc.)
    - Describe the action clearly
    - Mention the style (cinematic, realistic, etc.)
    - For dialogue, use quotes: "Hello there!"
    """)

with tips_col2:
    st.markdown("""
    **⚡ Technical Details:**
    - **Resolution:** 720p at 24fps
    - **Duration:** 8 seconds per video
    - **Audio:** Automatically generated
    - **Cost:** $0.75 per second ($6 per video)
    - **Generation Time:** 1-6 minutes
    """)

# Example prompts
with st.expander("📚 Example Prompts"):
    st.markdown("""
    **Tea Advertisement (Your Example):**
    ```
    A close-up shot of a single tea drop falling in slow motion into a steaming cup of tea, creating ripples. Golden hour lighting, warm tones, cinematic quality.
    ```
    
    **Nature Scene:**
    ```
    A majestic eagle soaring over snow-capped mountains, aerial view, golden sunset lighting, cinematic wide shot.
    ```
    
    **Urban Scene:**
    ```
    A bustling city street at night, neon lights reflecting on wet pavement, people walking, cinematic tracking shot, film noir style.
    ```
    
    **Product Demo:**
    ```
    A modern smartphone rotating slowly on a clean white surface, studio lighting, macro lens, product photography style.
    ```
    """)

# Success story section
st.markdown("---")
st.success("""
**✅ This interface uses the exact same code that works in your Jupyter notebook!**

The core video generation logic is identical to your working local code:
- Same imports: `from google import genai` and `from google.genai import types`
- Same client setup: `genai.Client(api_key=api_key)`
- Same generation call: `client.models.generate_videos()`
- Same polling loop: `while not operation.done:`
- Same download process: `generated_video.video.save()`
""")

# Warning about costs
st.warning("⚠️ **Cost Warning:** Each 8-second video costs $6 USD. Make sure you have sufficient billing credits in your Google Cloud project.")
#=====================================================================================================================================
# import streamlit as st
# import time
# import os
# import google.generativeai as genai
# import tempfile
# from datetime import datetime

# # Page configuration
# st.set_page_config(
#     page_title="Veo 3 Video Generator",
#     page_icon="🎬",
#     layout="wide"
# )

# # Title and description
# st.title("🎬 Veo 3 Video Generator")
# st.markdown("Generate high-quality 8-second videos with AI using Google's Veo 3 model")

# # Sidebar for API configuration
# with st.sidebar:
#     st.header("⚙️ Configuration")
#     api_key = st.text_input(
#         "Google AI API Key", 
#         type="password", 
#         help="Enter your Google AI API key",
#         placeholder="AIz..."
#     )
    
#     if api_key:
#         st.success("✅ API Key configured")
#     else:
#         st.warning("⚠️ Please enter your API key")

# # Main interface
# col1, col2 = st.columns([1, 1])

# with col1:
#     st.header("📝 Video Generation")
    
#     # Prompt input
#     prompt = st.text_area(
#         "Video Prompt",
#         height=100,
#         placeholder="Describe your video... e.g., 'A close-up shot of a tea drop falling into a steaming cup of tea, slow motion, warm lighting'",
#         help="Be descriptive! Include details about camera angles, lighting, actions, and style."
#     )
    
#     # Advanced options
#     with st.expander("🎛️ Advanced Options"):
#         negative_prompt = st.text_input(
#             "Negative Prompt (Optional)",
#             placeholder="Things to avoid... e.g., 'blurry, low quality, cartoon'",
#             help="Describe what you don't want in the video"
#         )
        
#         aspect_ratio = st.selectbox(
#             "Aspect Ratio",
#             ["16:9", "9:16"],
#             help="Choose video aspect ratio"
#         )
        
#         person_generation = st.selectbox(
#             "Person Generation",
#             ["allow_all", "allow_adult", "dont_allow"],
#             help="Control generation of people in videos"
#         )
    
#     # Generate button
#     generate_btn = st.button(
#         "🎬 Generate Video", 
#         type="primary", 
#         disabled=not (api_key and prompt),
#         use_container_width=True
#     )

# with col2:
#     st.header("🎥 Generated Video")
    
#     # Video display area
#     video_placeholder = st.empty()
    
#     # Initialize session state
#     if 'video_path' not in st.session_state:
#         st.session_state.video_path = None
#     if 'generating' not in st.session_state:
#         st.session_state.generating = False
#     if 'operation_id' not in st.session_state:
#         st.session_state.operation_id = None

# # Video generation logic
# if generate_btn and api_key and prompt:
#     st.session_state.generating = True
    
#     try:
#         # Configure genai
#         genai.configure(api_key=api_key)
        
#         # For now, we'll use a simplified approach since the new API might be different
#         # We'll show a message about using the correct API
#         st.error("🚧 **API Integration Notice**: The current Google GenerativeAI library may not support Veo 3 video generation through the standard `google-generativeai` package.")
#         st.info("📝 **Alternative Solutions:**")
#         st.markdown("""
#         1. **Use Google AI Studio directly** for video generation
#         2. **Use the REST API** with requests library
#         3. **Wait for official Python SDK update** for Veo 3 support
        
#         **For now, you can:**
#         - Copy your prompt and paste it in [Google AI Studio](https://aistudio.google.com)
#         - Use the Veo 3 Gallery there to generate videos
#         - Download the results manually
#         """)
        
#         st.session_state.generating = False
        
#     except Exception as e:
#         st.session_state.generating = False
#         st.error(f"❌ Error: {str(e)}")
#         st.info("💡 **Tip**: Try using the REST API approach or Google AI Studio directly.")

# # Alternative: REST API approach (placeholder for future implementation)
# if st.session_state.get('show_rest_example', False):
#     with st.expander("🔧 REST API Example (Advanced Users)"):
#         st.code("""
# import requests
# import json
# import time

# def generate_video_rest_api(api_key, prompt):
#     base_url = "https://generativelanguage.googleapis.com/v1beta"
    
#     # Start video generation
#     response = requests.post(
#         f"{base_url}/models/veo-3.0-generate-preview:predictLongRunning",
#         headers={
#             "x-goog-api-key": api_key,
#             "Content-Type": "application/json"
#         },
#         json={
#             "instances": [{"prompt": prompt}]
#         }
#     )
    
#     operation_name = response.json().get("name")
    
#     # Poll for completion
#     while True:
#         status_response = requests.get(
#             f"{base_url}/{operation_name}",
#             headers={"x-goog-api-key": api_key}
#         )
        
#         status = status_response.json()
#         if status.get("done"):
#             video_uri = status["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
#             return video_uri
        
#         time.sleep(10)
#         """, language="python")

# # Show generation status
# if st.session_state.generating:
#     with col2:
#         st.info("🎬 Processing request...")

# # Footer with tips
# st.markdown("---")
# st.markdown("### 💡 Pro Tips for Better Videos")

# tips_col1, tips_col2 = st.columns(2)

# with tips_col1:
#     st.markdown("""
#     **🎯 Prompt Writing Tips:**
#     - Be specific about camera angles (close-up, wide shot, etc.)
#     - Include lighting details (natural light, golden hour, etc.)
#     - Describe the action clearly
#     - Mention the style (cinematic, realistic, etc.)
#     - For dialogue, use quotes: "Hello there!"
#     """)

# with tips_col2:
#     st.markdown("""
#     **⚡ Technical Details:**
#     - **Resolution:** 720p at 24fps
#     - **Duration:** 8 seconds per video
#     - **Audio:** Automatically generated
#     - **Cost:** $0.75 per second ($6 per video)
#     - **Generation Time:** 1-6 minutes
#     """)

# # Example prompts
# with st.expander("📚 Example Prompts"):
#     st.markdown("""
#     **Tea Advertisement:**
#     ```
#     A close-up shot of a single tea drop falling in slow motion into a steaming cup of tea, creating ripples. Golden hour lighting, warm tones, cinematic quality.
#     ```
    
#     **Nature Scene:**
#     ```
#     A majestic eagle soaring over snow-capped mountains, aerial view, golden sunset lighting, cinematic wide shot.
#     ```
    
#     **Urban Scene:**
#     ```
#     A bustling city street at night, neon lights reflecting on wet pavement, people walking, cinematic tracking shot, film noir style.
#     ```
    
#     **Product Demo:**
#     ```
#     A modern smartphone rotating slowly on a clean white surface, studio lighting, macro lens, product photography style.
#     ```
#     """)

# # Quick fix section
# st.markdown("---")
# st.markdown("### 🛠️ Current Status & Workarounds")

# st.info("""
# **🚧 Current Issue**: The standard `google-generativeai` Python library doesn't yet fully support Veo 3 video generation in the way shown in our original code.

# **✅ Working Solutions**:
# 1. **Use Google AI Studio directly**: Visit [ai.google.dev](https://ai.google.dev) → Veo 3 Gallery
# 2. **REST API integration**: Implement direct HTTP calls (more complex)
# 3. **Wait for SDK update**: Google may update the Python SDK soon

# **💡 This interface is ready** - once the Python SDK supports Veo 3 properly, we can easily update the backend!
# """)

# # Show toggle for REST API example
# if st.button("🔧 Show REST API Example"):
#     st.session_state.show_rest_example = not st.session_state.get('show_rest_example', False)
#     st.rerun()

# # Warning about costs
# st.warning("⚠️ **Cost Warning:** Each 8-second video costs $6 USD. Make sure you have sufficient billing credits in your Google Cloud project.")







#==========================================================================================================================================
# import streamlit as st
# import time
# import os
# from google import genai
# from google.genai import types
# import tempfile
# from datetime import datetime

# # Page configuration
# st.set_page_config(
#     page_title="Veo 3 Video Generator",
#     page_icon="🎬",
#     layout="wide"
# )

# # Title and description
# st.title("🎬 Veo 3 Video Generator")
# st.markdown("Generate high-quality 8-second videos with AI using Google's Veo 3 model")

# # Sidebar for API configuration
# with st.sidebar:
#     st.header("⚙️ Configuration")
#     api_key = st.text_input(
#         "Google AI API Key", 
#         type="password", 
#         help="Enter your Google AI API key",
#         placeholder="AIz..."
#     )
    
#     if api_key:
#         st.success("✅ API Key configured")
#     else:
#         st.warning("⚠️ Please enter your API key")

# # Main interface
# col1, col2 = st.columns([1, 1])

# with col1:
#     st.header("📝 Video Generation")
    
#     # Prompt input
#     prompt = st.text_area(
#         "Video Prompt",
#         height=100,
#         placeholder="Describe your video... e.g., 'A close-up shot of a tea drop falling into a steaming cup of tea, slow motion, warm lighting'",
#         help="Be descriptive! Include details about camera angles, lighting, actions, and style."
#     )
    
#     # Advanced options
#     with st.expander("🎛️ Advanced Options"):
#         negative_prompt = st.text_input(
#             "Negative Prompt (Optional)",
#             placeholder="Things to avoid... e.g., 'blurry, low quality, cartoon'",
#             help="Describe what you don't want in the video"
#         )
        
#         aspect_ratio = st.selectbox(
#             "Aspect Ratio",
#             ["16:9", "9:16"],
#             help="Choose video aspect ratio"
#         )
        
#         person_generation = st.selectbox(
#             "Person Generation",
#             ["allow_all", "allow_adult", "dont_allow"],
#             help="Control generation of people in videos"
#         )
    
#     # Generate button
#     generate_btn = st.button(
#         "🎬 Generate Video", 
#         type="primary", 
#         disabled=not (api_key and prompt),
#         use_container_width=True
#     )

# with col2:
#     st.header("🎥 Generated Video")
    
#     # Video display area
#     video_placeholder = st.empty()
    
#     # Initialize session state
#     if 'video_path' not in st.session_state:
#         st.session_state.video_path = None
#     if 'generating' not in st.session_state:
#         st.session_state.generating = False
#     if 'operation_id' not in st.session_state:
#         st.session_state.operation_id = None

# # Video generation logic
# if generate_btn and api_key and prompt:
#     st.session_state.generating = True
    
#     try:
#         # Configure client
#         client = genai.Client(api_key=api_key)
        
#         # Prepare config
#         config_params = {}
#         if negative_prompt:
#             config_params['negative_prompt'] = negative_prompt
#         if aspect_ratio:
#             config_params['aspect_ratio'] = aspect_ratio
#         if person_generation:
#             config_params['person_generation'] = person_generation
            
#         config = types.GenerateVideosConfig(**config_params) if config_params else None
        
#         with st.spinner("🚀 Starting video generation..."):
#             # Start video generation
#             operation = client.models.generate_videos(
#                 model="veo-3.0-generate-preview",
#                 prompt=prompt,
#                 config=config
#             )
            
#             st.session_state.operation_id = operation.name
#             st.success(f"✅ Video generation started! Operation ID: {operation.name}")
        
#         # Progress tracking
#         progress_bar = st.progress(0)
#         status_text = st.empty()
#         time_elapsed = st.empty()
        
#         start_time = time.time()
        
#         # Poll for completion
#         while not operation.done:
#             elapsed = int(time.time() - start_time)
#             time_elapsed.text(f"⏱️ Time elapsed: {elapsed} seconds")
            
#             # Update progress (estimated)
#             if elapsed < 60:
#                 progress = min(elapsed / 60, 0.9)  # Max 90% until actually done
#             else:
#                 progress = 0.9
            
#             progress_bar.progress(progress)
#             status_text.info("🎬 Generating your video... This may take 1-6 minutes depending on server load.")
            
#             time.sleep(10)
#             operation = client.operations.get(operation)
        
#         # Complete progress
#         progress_bar.progress(1.0)
#         elapsed = int(time.time() - start_time)
#         time_elapsed.text(f"✅ Generation completed in {elapsed} seconds!")
#         status_text.success("🎉 Video generation completed!")
        
#         # Download and save video
#         with st.spinner("📥 Downloading video..."):
#             generated_video = operation.response.generated_videos[0]
            
#             # Create temporary file for video
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             temp_dir = tempfile.gettempdir()
#             video_filename = f"veo3_video_{timestamp}.mp4"
#             video_path = os.path.join(temp_dir, video_filename)
            
#             # Download video
#             client.files.download(file=generated_video.video)
#             generated_video.video.save(video_path)
            
#             st.session_state.video_path = video_path
#             st.session_state.generating = False
            
#         st.success("🎉 Video ready for viewing and download!")
#         st.rerun()
        
#     except Exception as e:
#         st.session_state.generating = False
#         st.error(f"❌ Error generating video: {str(e)}")
#         st.error("Please check your API key and try again.")

# # Display video if available
# if st.session_state.video_path and os.path.exists(st.session_state.video_path):
#     with col2:
#         st.success("🎉 Your video is ready!")
        
#         # Display video
#         with open(st.session_state.video_path, 'rb') as video_file:
#             video_bytes = video_file.read()
#             st.video(video_bytes)
        
#         # Video info
#         file_size = os.path.getsize(st.session_state.video_path) / (1024 * 1024)  # MB
#         st.info(f"📊 Video Info: 720p, 8 seconds, {file_size:.2f} MB")
        
#         # Download button
#         with open(st.session_state.video_path, 'rb') as video_file:
#             st.download_button(
#                 label="⬇️ Download Video",
#                 data=video_file.read(),
#                 file_name=f"veo3_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
#                 mime="video/mp4",
#                 type="primary",
#                 use_container_width=True
#             )

# # Show generation status
# if st.session_state.generating:
#     with col2:
#         st.info("🎬 Video is being generated... Please wait.")

# # Footer with tips
# st.markdown("---")
# st.markdown("### 💡 Pro Tips for Better Videos")

# tips_col1, tips_col2 = st.columns(2)

# with tips_col1:
#     st.markdown("""
#     **🎯 Prompt Writing Tips:**
#     - Be specific about camera angles (close-up, wide shot, etc.)
#     - Include lighting details (natural light, golden hour, etc.)
#     - Describe the action clearly
#     - Mention the style (cinematic, realistic, etc.)
#     - For dialogue, use quotes: "Hello there!"
#     """)

# with tips_col2:
#     st.markdown("""
#     **⚡ Technical Details:**
#     - **Resolution:** 720p at 24fps
#     - **Duration:** 8 seconds per video
#     - **Audio:** Automatically generated
#     - **Cost:** $0.75 per second ($6 per video)
#     - **Generation Time:** 1-6 minutes
#     """)

# # Example prompts
# with st.expander("📚 Example Prompts"):
#     st.markdown("""
#     **Tea Advertisement:**
#     ```
#     A close-up shot of a single tea drop falling in slow motion into a steaming cup of tea, creating ripples. Golden hour lighting, warm tones, cinematic quality.
#     ```
    
#     **Nature Scene:**
#     ```
#     A majestic eagle soaring over snow-capped mountains, aerial view, golden sunset lighting, cinematic wide shot.
#     ```
    
#     **Urban Scene:**
#     ```
#     A bustling city street at night, neon lights reflecting on wet pavement, people walking, cinematic tracking shot, film noir style.
#     ```
    
#     **Product Demo:**
#     ```
#     A modern smartphone rotating slowly on a clean white surface, studio lighting, macro lens, product photography style.
#     ```
#     """)

# # Warning about costs
# st.warning("⚠️ **Cost Warning:** Each 8-second video costs $6 USD. Make sure you have sufficient billing credits in your Google Cloud project.")
