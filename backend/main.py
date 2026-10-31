# ============================================================
# TRUSTLENS AI - FASTAPI BACKEND
# Text + Image + Video + Multimodal News Analysis
# ============================================================

import os
import json
import base64
import time
import tempfile

from pathlib import Path

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from google import genai


# LOAD ENVIRONMENT VARIABLES

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

# Do not stop application startup when the secret is missing.
# FastAPI Cloud can still complete its readiness check; analysis
# endpoints return a clear error until GEMINI_API_KEY is configured.


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=api_key) if api_key else None


def require_gemini_client():
    """Return the Gemini client or raise a clear configuration error."""
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured. Add it to FastAPI Cloud secrets."
        )
    return client


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="TrustLens AI",
    description=(
        "AI-powered fake news, image, video and "
        "multimodal content verification system"
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5501,http://localhost:5501,"
        "http://127.0.0.1:5500,http://localhost:5500"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL - TEXT
# ============================================================

class NewsRequest(BaseModel):

    news_text: str = Field(
        min_length=10,
        max_length=10000,
        description="News content to analyze"
    )


# ============================================================
# RESPONSE MODEL
# ============================================================

class AnalysisResult(BaseModel):

    classification: str

    confidence: int

    trust_score: int

    explanation: str

    key_concerns: list[str]

    verification_status: str

    recommendation: str


class AnalysisResponse(BaseModel):

    success: bool

    result: AnalysisResult


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to TrustLens AI API",
        "status": "Server is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "TrustLens AI"
    }


# ============================================================
# COMMON AI RESULT VALIDATION
# ============================================================

def validate_result(result: dict):

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    allowed_classifications = [
        "Likely Real",
        "Likely Fake",
        "Uncertain"
    ]

    if result.get("classification") not in allowed_classifications:

        result["classification"] = "Uncertain"


    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    try:

        confidence = int(
            result.get(
                "confidence",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        confidence = 0


    result["confidence"] = max(
        0,
        min(
            100,
            confidence
        )
    )


    # --------------------------------------------------------
    # TRUST SCORE
    # --------------------------------------------------------

    try:

        trust_score = int(
            result.get(
                "trust_score",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        trust_score = 0


    result["trust_score"] = max(
        0,
        min(
            100,
            trust_score
        )
    )


    # --------------------------------------------------------
    # VERIFICATION STATUS
    # --------------------------------------------------------

    allowed_verification_status = [

        "Verified",

        "Needs Further Verification",

        "Insufficient Evidence"
    ]


    if (
        result.get(
            "verification_status"
        )
        not in allowed_verification_status
    ):

        result["verification_status"] = (
            "Needs Further Verification"
        )


    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    if not result.get(
        "explanation"
    ):

        result["explanation"] = (
            "No explanation was provided."
        )


    # --------------------------------------------------------
    # KEY CONCERNS
    # --------------------------------------------------------

    if not isinstance(
        result.get("key_concerns"),
        list
    ):

        result["key_concerns"] = []


    result["key_concerns"] = [

        str(item)

        for item in result[
            "key_concerns"
        ]
    ]


    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    if not result.get(
        "recommendation"
    ):

        result["recommendation"] = (
            "Check reliable and official sources "
            "before sharing this information."
        )


    return result


# ============================================================
# JSON CLEANING HELPER
# ============================================================

def clean_json_response(response_text: str):

    if not response_text:

        raise ValueError(
            "Gemini returned an empty response."
        )


    response_text = response_text.strip()


    # --------------------------------------------------------
    # REMOVE MARKDOWN CODE BLOCK
    # --------------------------------------------------------

    if response_text.startswith("```json"):

        response_text = response_text[7:]


    elif response_text.startswith("```"):

        response_text = response_text[3:]


    if response_text.endswith("```"):

        response_text = response_text[:-3]


    response_text = response_text.strip()


    return response_text


# ============================================================
# TEXT ANALYSIS
# ============================================================

@app.post(
    "/analyze-text",
    response_model=AnalysisResponse
)
def analyze_text(
    request: NewsRequest
):
    require_gemini_client()

    prompt = f"""
You are TrustLens AI, an AI-powered news credibility
assessment system.

Analyze the following news claim carefully.

NEWS CONTENT:

{request.news_text}

Evaluate:

- wording
- evidence
- plausibility
- attribution
- possible misinformation indicators
- unsupported claims
- sensational language
- missing sources

Do not automatically assume the claim is real or fake.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "classification": "Likely Real",
    "confidence": 0,
    "trust_score": 0,
    "explanation": "Short clear explanation",
    "key_concerns": [
        "Concern 1",
        "Concern 2"
    ],
    "verification_status": "Needs Further Verification",
    "recommendation": "Check reliable official sources before sharing this claim."
}}

RULES:

1. classification must be exactly one of:

   Likely Real
   Likely Fake
   Uncertain

2. confidence must be an integer from 0 to 100.

3. trust_score must be an integer from 0 to 100.

4. verification_status must be exactly one of:

   Verified
   Needs Further Verification
   Insufficient Evidence

5. recommendation must give the user a useful next action.

6. explanation must clearly explain the classification.

7. key_concerns must be a JSON list.

8. Do not use Markdown.

9. Do not return ```json.

10. Return JSON only.
"""


    response_text = ""


    try:

        interaction = client.interactions.create(

            model="gemini-3.6-flash",

            input=prompt
        )


        response_text = (
            interaction.output_text
        )


        response_text = clean_json_response(
            response_text
        )


        result = json.loads(
            response_text
        )


        result = validate_result(
            result
        )


        return {

            "success": True,

            "result": result
        }


    except json.JSONDecodeError:

        raise HTTPException(

            status_code=500,

            detail={
                "message":
                    "AI did not return valid JSON.",

                "raw_response":
                    response_text
            }
        )


    except Exception as e:

        print(
            "GEMINI TEXT ERROR:",
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=(
                "AI text analysis failed: "
                f"{str(e)}"
            )
        )


# ============================================================
# IMAGE ANALYSIS - PHASE 4
# ============================================================

@app.post(
    "/analyze-image"
)
async def analyze_image(

    file: UploadFile = File(...),

    context: str = Form("")
):

    if not api_key:

        raise HTTPException(

            status_code=500,

            detail="GEMINI_API_KEY not found."
        )


    allowed_types = [

        "image/jpeg",

        "image/png",

        "image/webp",

        "image/jpg"
    ]


    if file.content_type not in allowed_types:

        raise HTTPException(

            status_code=400,

            detail=(
                "Unsupported image type. "
                "Please upload JPG, JPEG, PNG or WEBP."
            )
        )


    response_text = ""


    try:

        image_bytes = await file.read()


        if not image_bytes:

            raise HTTPException(

                status_code=400,

                detail="Uploaded image is empty."
            )


        max_size = (
            10 * 1024 * 1024
        )


        if len(image_bytes) > max_size:

            raise HTTPException(

                status_code=400,

                detail=(
                    "Image size must be less than 10 MB."
                )
            )


        image_base64 = (
            base64.b64encode(
                image_bytes
            ).decode("utf-8")
        )


        image_prompt = f"""
You are TrustLens AI, an AI-powered misinformation
and fake-news detection system.

Analyze the uploaded news image.

The image may contain:

- a news screenshot
- social media post
- newspaper clipping
- headline
- news card
- quotation
- photograph
- misleading visual content
- fabricated claim

Analyze the visible text and visual context carefully.

Look for:

1. Suspicious headlines
2. Sensational language
3. Missing source information
4. Manipulated or misleading context
5. Unsupported claims
6. Fake-looking news layouts
7. Contradictory information
8. Potentially misleading images
9. Missing date or attribution
10. Other misinformation indicators

IMPORTANT:

Do not claim that an image is definitely fake only because
it looks suspicious.

If there is insufficient evidence, use "Uncertain".

{f"Additional context provided by user: {context}" if context else ""}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "classification": "Likely Real",
    "confidence": 0,
    "trust_score": 0,
    "explanation": "Short explanation based on the image.",
    "key_concerns": [
        "Concern 1",
        "Concern 2"
    ],
    "verification_status": "Needs Further Verification",
    "recommendation": "Verify the claim using reliable sources."
}}

RULES:

1. classification must be exactly one of:

   Likely Real
   Likely Fake
   Uncertain

2. confidence must be an integer from 0 to 100.

3. trust_score must be an integer from 0 to 100.

4. verification_status must be exactly one of:

   Verified
   Needs Further Verification
   Insufficient Evidence

5. key_concerns must be a JSON list.

6. explanation must be clear and understandable.

7. recommendation must provide a useful next action.

8. Do not use Markdown.

9. Do not return ```json.

10. Return JSON only.
"""


        interaction = client.interactions.create(

            model="gemini-3.6-flash",

            input=[

                {
                    "type": "text",

                    "text": image_prompt
                },

                {
                    "type": "image",

                    "data": image_base64,

                    "mime_type":
                        file.content_type
                }
            ]
        )


        response_text = (
            interaction.output_text
        )


        response_text = clean_json_response(
            response_text
        )


        result = json.loads(
            response_text
        )


        result = validate_result(
            result
        )


        return {

            "success": True,

            "analysis_type": "image",

            "filename":
                file.filename,

            "content_type":
                file.content_type,

            "result":
                result
        }


    except json.JSONDecodeError:

        raise HTTPException(

            status_code=500,

            detail={
                "message":
                    "AI did not return valid JSON.",

                "raw_response":
                    response_text
            }
        )


    except HTTPException:

        raise


    except Exception as e:

        print(
            "GEMINI IMAGE ERROR:",
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=(
                "AI image analysis failed: "
                f"{str(e)}"
            )
        )


# ============================================================
# VIDEO ANALYSIS - PHASE 5
# ============================================================

@app.post(
    "/analyze-video"
)
async def analyze_video(

    file: UploadFile = File(...),

    context: str = Form("")
):

    if not api_key:

        raise HTTPException(

            status_code=500,

            detail="GEMINI_API_KEY not found."
        )


    if not file:

        raise HTTPException(

            status_code=400,

            detail="No video file received."
        )


    allowed_types = [

        "video/mp4",

        "video/webm",

        "video/quicktime",

        "video/x-msvideo"
    ]


    if file.content_type not in allowed_types:

        raise HTTPException(

            status_code=400,

            detail=(
                "Unsupported video format. "
                "Please upload MP4, WebM, MOV or AVI."
            )
        )


    video_bytes = await file.read()


    if not video_bytes:

        raise HTTPException(

            status_code=400,

            detail="Uploaded video is empty."
        )


    max_size = (
        50 * 1024 * 1024
    )


    if len(video_bytes) > max_size:

        raise HTTPException(

            status_code=413,

            detail=(
                "Video size must not exceed 50 MB."
            )
        )


    suffix = Path(
        file.filename or "video.mp4"
    ).suffix


    if not suffix:

        suffix = ".mp4"


    temp_path = None

    response_text = ""


    try:

        with tempfile.NamedTemporaryFile(

            delete=False,

            suffix=suffix

        ) as temp_file:

            temp_file.write(
                video_bytes
            )

            temp_path = (
                temp_file.name
            )


        print(
            "Temporary video:",
            temp_path
        )


        video_client = genai.Client(

            api_key=api_key
        )


        print(
            "Uploading video to Gemini..."
        )


        uploaded_file = (
            video_client.files.upload(
                file=temp_path
            )
        )


        print(
            "Gemini file:",
            uploaded_file.name
        )


        max_wait_time = 180

        waited = 0


        while True:

            current_file = (
                video_client.files.get(
                    name=uploaded_file.name
                )
            )


            if current_file.state:

                state = (
                    current_file.state.name
                )

            else:

                state = "UNKNOWN"


            print(
                "Video processing state:",
                state
            )


            if state == "ACTIVE":

                uploaded_file = (
                    current_file
                )

                break


            if state == "FAILED":

                raise RuntimeError(
                    "Gemini failed to process the video."
                )


            if waited >= max_wait_time:

                raise TimeoutError(
                    "Video processing timed out."
                )


            time.sleep(3)

            waited += 3


        prompt = f"""
You are TrustLens AI, an AI-powered
video news credibility assessment system.

Analyze the uploaded video carefully.

Evaluate:

1. Visual content
2. Claims presented in the video
3. On-screen text
4. Context and consistency
5. Signs of misleading editing
6. Suspicious or unsupported claims
7. Whether the video appears manipulated,
   misleading, or taken out of context
8. Additional context supplied by the user

USER CONTEXT:

{context if context else "No additional context provided."}

IMPORTANT:

Do not automatically classify the video as real or fake.

Base the assessment on the available evidence.

If there is insufficient evidence, use "Uncertain".

Return ONLY valid JSON.

Use exactly this structure:

{{
    "classification": "Likely Real",
    "confidence": 0,
    "trust_score": 0,
    "explanation": "Short clear explanation",
    "key_concerns": [
        "Concern 1",
        "Concern 2"
    ],
    "verification_status": "Needs Further Verification",
    "recommendation": "Check reliable sources before sharing this video."
}}

RULES:

1. classification must be exactly one of:

   Likely Real
   Likely Fake
   Uncertain

2. confidence must be an integer from 0 to 100.

3. trust_score must be an integer from 0 to 100.

4. verification_status must be exactly one of:

   Verified
   Needs Further Verification
   Insufficient Evidence

5. key_concerns must be a JSON array.

6. explanation must be clear.

7. recommendation must provide a useful next action.

8. Do not use Markdown.

9. Do not return ```json.

10. Return JSON only.
"""


        print(
            "Analyzing video with Gemini..."
        )


        interaction = (
            video_client.interactions.create(

                model="gemini-3.6-flash",

                input=[

                    {
                        "type": "video",

                        "uri":
                            uploaded_file.uri,

                        "mime_type":
                            uploaded_file.mime_type
                    },

                    {
                        "type": "text",

                        "text":
                            prompt
                    }
                ]
            )
        )


        response_text = (
            interaction.output_text
        )


        response_text = clean_json_response(
            response_text
        )


        result = json.loads(
            response_text
        )


        result = validate_result(
            result
        )


        return {

            "success": True,

            "analysis_type": "video",

            "filename":
                file.filename,

            "content_type":
                file.content_type,

            "result":
                result
        }


    except json.JSONDecodeError:

        raise HTTPException(

            status_code=500,

            detail={

                "message":
                    "Gemini did not return valid JSON.",

                "raw_response":
                    response_text
            }
        )


    except HTTPException:

        raise


    except Exception as e:

        print(
            "GEMINI VIDEO ERROR:",
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=(
                "Video analysis failed: "
                f"{str(e)}"
            )
        )


    finally:

        if temp_path:

            try:

                os.remove(
                    temp_path
                )

                print(
                    "Temporary video deleted."
                )

            except OSError:

                pass


# ============================================================
# MULTIMODAL ANALYSIS - PHASE 6
# ============================================================

@app.post(
    "/analyze-multimodal"
)
async def analyze_multimodal(

    news_text: str = Form(""),

    image: UploadFile | None = File(None),

    video: UploadFile | None = File(None)

):
    """
    TrustLens AI Multimodal Analysis.

    Supported combinations:

    1. Text only
    2. Text + Image
    3. Text + Video
    4. Text + Image + Video
    5. Image only
    6. Video only

    The system performs cross-modal reasoning when
    multiple modalities are supplied.
    """

    require_gemini_client()

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if (
        not news_text.strip()
        and image is None
        and video is None
    ):

        raise HTTPException(

            status_code=400,

            detail=(
                "Please provide at least one input: "
                "text, image or video."
            )
        )


    # ========================================================
    # SIZE LIMITS
    # ========================================================

    max_image_size = (
        10 * 1024 * 1024
    )

    max_video_size = (
        50 * 1024 * 1024
    )


    # ========================================================
    # TEMPORARY VIDEO PATH
    # ========================================================

    temp_video_path = None

    response_text = ""


    try:

        # ====================================================
        # MODALITY FLAGS
        # ====================================================

        has_text = bool(
            news_text.strip()
        )

        has_image = (
            image is not None
        )

        has_video = (
            video is not None
        )


        # ====================================================
        # BUILD MODALITY DESCRIPTION
        # ====================================================

        modalities = []


        if has_text:

            modalities.append(
                "TEXT"
            )


        if has_image:

            modalities.append(
                "IMAGE"
            )


        if has_video:

            modalities.append(
                "VIDEO"
            )


        modality_description = (
            ", ".join(modalities)
        )


        print(
            "Multimodal inputs:",
            modality_description
        )


        # ====================================================
        # GEMINI INPUT
        # ====================================================

        gemini_input = []


        # ====================================================
        # TEXT
        # ====================================================

        if has_text:

            gemini_input.append({

                "type": "text",

                "text":
                    f"""
NEWS CLAIM / CONTEXT:

{news_text}
"""
            })


        # ====================================================
        # IMAGE
        # ====================================================

        if has_image:

            allowed_image_types = [

                "image/jpeg",

                "image/png",

                "image/webp",

                "image/jpg"
            ]


            if image.content_type not in allowed_image_types:

                raise HTTPException(

                    status_code=400,

                    detail=(
                        "Unsupported image type. "
                        "Please upload JPG, JPEG, PNG or WEBP."
                    )
                )


            image_bytes = await image.read()


            if not image_bytes:

                raise HTTPException(

                    status_code=400,

                    detail="Uploaded image is empty."
                )


            if len(image_bytes) > max_image_size:

                raise HTTPException(

                    status_code=400,

                    detail=(
                        "Image size must be less than 10 MB."
                    )
                )


            image_base64 = (
                base64.b64encode(
                    image_bytes
                ).decode("utf-8")
            )


            gemini_input.append({

                "type": "image",

                "data":
                    image_base64,

                "mime_type":
                    image.content_type
            })


        # ====================================================
        # VIDEO
        # ====================================================

        if has_video:

            allowed_video_types = [

                "video/mp4",

                "video/webm",

                "video/quicktime",

                "video/x-msvideo"
            ]


            if video.content_type not in allowed_video_types:

                raise HTTPException(

                    status_code=400,

                    detail=(
                        "Unsupported video format. "
                        "Please upload MP4, WebM, MOV or AVI."
                    )
                )


            video_bytes = await video.read()


            if not video_bytes:

                raise HTTPException(

                    status_code=400,

                    detail="Uploaded video is empty."
                )


            if len(video_bytes) > max_video_size:

                raise HTTPException(

                    status_code=413,

                    detail=(
                        "Video size must not exceed 50 MB."
                    )
                )


            suffix = Path(
                video.filename or "video.mp4"
            ).suffix


            if not suffix:

                suffix = ".mp4"


            # ----------------------------------------------
            # CREATE TEMP VIDEO
            # ----------------------------------------------

            with tempfile.NamedTemporaryFile(

                delete=False,

                suffix=suffix

            ) as temp_file:

                temp_file.write(
                    video_bytes
                )

                temp_video_path = (
                    temp_file.name
                )


            print(
                "Multimodal temporary video:",
                temp_video_path
            )


            # ----------------------------------------------
            # UPLOAD VIDEO
            # ----------------------------------------------

            print(
                "Uploading multimodal video to Gemini..."
            )


            uploaded_video = (
                client.files.upload(
                    file=temp_video_path
                )
            )


            print(
                "Multimodal Gemini file:",
                uploaded_video.name
            )


            # ----------------------------------------------
            # WAIT FOR PROCESSING
            # ----------------------------------------------

            max_wait_time = 180

            waited = 0


            while True:

                current_file = (
                    client.files.get(
                        name=uploaded_video.name
                    )
                )


                if current_file.state:

                    state = (
                        current_file.state.name
                    )

                else:

                    state = "UNKNOWN"


                print(
                    "Multimodal video state:",
                    state
                )


                if state == "ACTIVE":

                    uploaded_video = (
                        current_file
                    )

                    break


                if state == "FAILED":

                    raise RuntimeError(
                        "Gemini failed to process the multimodal video."
                    )


                if waited >= max_wait_time:

                    raise TimeoutError(
                        "Multimodal video processing timed out."
                    )


                time.sleep(3)

                waited += 3


            # ----------------------------------------------
            # ADD VIDEO TO GEMINI INPUT
            # ----------------------------------------------

            gemini_input.append({

                "type": "video",

                "uri":
                    uploaded_video.uri,

                "mime_type":
                    uploaded_video.mime_type
            })


        # ====================================================
        # MULTIMODAL ANALYSIS PROMPT
        # ====================================================

        multimodal_prompt = f"""
You are TrustLens AI, a multimodal news credibility
assessment and misinformation analysis system.

AVAILABLE MODALITIES:

{modality_description}

Your task is to analyze the supplied news content
using ALL available modalities together.

Do NOT simply perform independent analyses.

Perform CROSS-MODAL REASONING.

============================================================
1. TEXT ANALYSIS
============================================================

If text is available, evaluate:

- claim wording
- factual assertions
- source attribution
- evidence
- sensational language
- unsupported statements
- suspicious claims
- missing context

============================================================
2. IMAGE ANALYSIS
============================================================

If an image is available, evaluate:

- visible text
- headline
- visual context
- source information
- date
- logos
- apparent manipulation
- misleading presentation
- whether the image supports the claim

============================================================
3. VIDEO ANALYSIS
============================================================

If a video is available, evaluate:

- visual content
- spoken claims
- on-screen text
- context
- apparent editing
- possible manipulation
- whether the video supports the claim

============================================================
4. CROSS-MODAL CONSISTENCY
============================================================

When multiple modalities are available, compare them.

Determine whether:

- text supports the image
- text supports the video
- image supports the video
- dates appear consistent
- locations appear consistent
- people/events appear consistent
- claims contradict visual evidence
- content appears unrelated
- important context is missing

Identify contradictions explicitly.

Do not invent contradictions when there is insufficient
evidence.

============================================================
5. FINAL ASSESSMENT
============================================================

Provide:

- overall classification
- confidence
- unified trust score
- verification status
- explanation
- key concerns
- recommendation
- analysis of each available modality
- cross-modal consistency
- contradictions

IMPORTANT:

The Trust Score should represent the credibility of the
available evidence, not simply whether the content looks
professional.

If evidence is insufficient, use "Uncertain".

Do not claim external verification unless actual
verification evidence is provided.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "classification": "Likely Real",

    "confidence": 0,

    "trust_score": 0,

    "explanation": "Overall explanation of the analysis.",

    "key_concerns": [
        "Concern 1",
        "Concern 2"
    ],

    "verification_status": "Needs Further Verification",

    "recommendation": "Useful next step for the user.",

    "modal_analysis": {{
        "text": "Text analysis result.",
        "image": "Image analysis result.",
        "video": "Video analysis result."
    }},

    "cross_modal_consistency": "High",

    "contradictions": [
        "Contradiction 1"
    ]
}}

RULES:

1. classification must be exactly one of:

   Likely Real
   Likely Fake
   Uncertain

2. confidence must be an integer from 0 to 100.

3. trust_score must be an integer from 0 to 100.

4. verification_status must be exactly one of:

   Verified
   Needs Further Verification
   Insufficient Evidence

5. cross_modal_consistency must be exactly one of:

   High
   Medium
   Low
   Not Applicable

6. key_concerns must be a JSON array.

7. contradictions must be a JSON array.

8. modal_analysis must contain:

   text
   image
   video

9. If a modality was not provided, write:

   "Not provided."

10. Do not use Markdown.

11. Do not return ```json.

12. Return JSON only.
"""


        # ====================================================
        # ADD FINAL INSTRUCTION
        # ====================================================

        gemini_input.append({

            "type": "text",

            "text":
                multimodal_prompt
        })


        # ====================================================
        # CALL GEMINI
        # ====================================================

        print(
            "Running multimodal analysis with Gemini..."
        )


        interaction = (
            client.interactions.create(

                model="gemini-3.6-flash",

                input=gemini_input
            )
        )


        # ====================================================
        # GET RESPONSE
        # ====================================================

        response_text = (
            interaction.output_text
        )


        response_text = clean_json_response(
            response_text
        )


        # ====================================================
        # PARSE JSON
        # ====================================================

        result = json.loads(
            response_text
        )


        # ====================================================
        # VALIDATE COMMON RESULT
        # ====================================================

        result = validate_result(
            result
        )


        # ====================================================
        # VALIDATE MULTIMODAL FIELDS
        # ====================================================

        if not isinstance(
            result.get("modal_analysis"),
            dict
        ):

            result["modal_analysis"] = {}


        modal_analysis = (
            result["modal_analysis"]
        )


        modal_analysis.setdefault(
            "text",
            "Not provided."
        )

        modal_analysis.setdefault(
            "image",
            "Not provided."
        )

        modal_analysis.setdefault(
            "video",
            "Not provided."
        )


        if result.get(
            "cross_modal_consistency"
        ) not in [

            "High",

            "Medium",

            "Low",

            "Not Applicable"
        ]:

            result[
                "cross_modal_consistency"
            ] = (
                "Not Applicable"
            )


        if not isinstance(
            result.get("contradictions"),
            list
        ):

            result["contradictions"] = []


        result["contradictions"] = [

            str(item)

            for item in result[
                "contradictions"
            ]
        ]


        # ====================================================
        # RETURN RESULT
        # ====================================================

        return {

            "success": True,

            "analysis_type":
                "multimodal",

            "modalities": {

                "text":
                    has_text,

                "image":
                    has_image,

                "video":
                    has_video
            },

            "result":
                result
        }


    # ========================================================
    # JSON ERROR
    # ========================================================

    except json.JSONDecodeError:

        raise HTTPException(

            status_code=500,

            detail={

                "message":
                    "Gemini did not return valid JSON.",

                "raw_response":
                    response_text
            }
        )


    # ========================================================
    # HTTP ERROR
    # ========================================================

    except HTTPException:

        raise


    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as e:

        print(
            "GEMINI MULTIMODAL ERROR:",
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=(
                "Multimodal analysis failed: "
                f"{str(e)}"
            )
        )


    # ========================================================
    # CLEAN TEMP VIDEO
    # ========================================================

    finally:

        if temp_video_path:

            try:

                os.remove(
                    temp_video_path
                )

                print(
                    "Multimodal temporary video deleted."
                )

            except OSError:

                pass
