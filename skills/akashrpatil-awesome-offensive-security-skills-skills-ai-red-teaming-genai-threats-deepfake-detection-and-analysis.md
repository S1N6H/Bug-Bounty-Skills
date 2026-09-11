---
name: deepfake-detection-and-analysis
description: >
  Analyze and detect synthetic media, including deepfake videos, AI-generated images, and cloned
  voice audio. Use this skill when investigating potential disinformation campaigns, verifying
  the authenticity of digital evidence, or assessing social engineering attacks leveraging
  synthetic media (e.g., vishing with voice clones, spear-phishing with deepfake video calls).
  Covers artifact analysis, frequency detection, metadata tracing, and automated detection tools.
domain: cybersecurity
subdomain: ai-red-teaming
category: GenAI Threats
difficulty: advanced
estimated_time: "4-8 hours"
mitre_atlas:
  tactics: [AML.TA0001]
  techniques: [AML.T0043, AML.T0051]
mitre_attack:
  tactics: [TA0001, TA0040]
  techniques: [AML.T0048, T1598, T1056]
platforms: [linux, windows, macos]
tags: [deepfake, synthetic-media, ai-voice-clone, disinformation, forensics, incident-response, vishing]
tools: [python, deepware-api, exiftool, dlib, ffmpeg, librosa]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
---

# Deepfake Detection & Analysis

## When to Use
- When verifying the authenticity of sensitive media (executives, political figures)
- During incident response for CEO impersonation / BEC scams using voice cloning
- When investigating disinformation or influence operations
- When training corporate teams on deepfake recognition
- When building defensive pipelines for media upload portals


## Prerequisites
- Access to target AI/ML system or local model deployment for testing
- Python 3.9+ with relevant ML libraries (transformers, torch, openai)
- Understanding of LLM architecture and prompt processing pipelines
- Authorized scope and rules of engagement for AI red team testing

## Workflow

### Phase 1: Visual Artifact Inspection (Manual)

```bash
# Extract frames from video for detailed analysis
ffmpeg -i suspicious_video.mp4 -vf fps=1/1 out%04d.png

# Look for these common visual artifacts:
# 1. Blinking anomalies (too much, too little, unnatural eyelids)
# 2. Lighting/Shadow inconsistencies (face lighting differs from background)
# 3. Blurring or edge artifacts around the face perimeter (the "mask" line)
# 4. Unnatural teeth rendering (AI struggles with individual teeth)
# 5. Mismatched skin tones or unnatural smoothness
# 6. Glitches during rapid movement or hand occlusion (hands passing in front of face)
# 7. Asymmetrical reflections in the eyes
```

### Phase 2: Metadata & Provenance Analysis

```bash
# Check EXIF and metadata for manipulation traces
exiftool suspicious_media.jpg
exiftool suspicious_video.mp4

# Look for:
# - Missing standard camera metadata (Make, Model)
# - Software signatures (e.g., Photoshop, AfterEffects, Stable Diffusion)
# - Mismatched timestamps (creation vs. modification)
# - Missing or altered GPS data

# Check for C2PA (Coalition for Content Provenance and Authenticity) manifests
# Many legitimate AI tools now embed watermarks or provenance data

# Search for the source media (Reverse Image Search)
# Provide the isolated face or background to Yandex/Google images
# to find the original unaltered source material
```

### Phase 3: Automated Image/Video Detection

```python
# Use Python and OpenCV/Dlib/PyTorch for automated detection

import cv2
import dlib
import numpy as np
# from deepfake_models import load_detector (example API)

def extract_face_landmarks(image_path):
    """Analyze facial landmarks for unnatural positioning or jitter over time."""
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    for face in faces:
        landmarks = predictor(gray, face)
        # Analyze symmetry and proportions
        # Deepfakes often disrupt natural biometric ratios

# Frequency domain analysis
# Deepfakes often lack high-frequency details present in real images
def frequency_analysis(image_path):
    img = cv2.imread(image_path, 0)
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20*np.log(np.abs(fshift))
    # Analyze magnitude spectrum for distinct GAN/diffusion artifacts
```

### Phase 4: Voice Clone (Audio) Analysis

```python
# Audio analysis is critical for modern vishing attacks

import librosa
import numpy as np

def analyze_audio_artifacts(audio_path):
    # Load audio
    y, sr = librosa.load(audio_path)
    
    # 1. Check for unnatural breathing patterns
    # AI voices often lack breaths, or place them unnaturally
    
    # 2. Spectrogram analysis
    # Look for frequency cutoffs (synthetic voices often drop frequencies above 10kHz)
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    
    # 3. Analyze pacing and emotion
    # Does the emotion match the semantic content?
    
    # 4. Check for robotic metallic ringing (vocoder artifacts)
    # Common in older or fast-generated voice clones

# Use commercial/open-source detection APIs
# e.g., Resemble AI Detect, AI Voice Detector
```

### Phase 5: Assessing the Delivery Mechanism

```bash
# Deepfakes are rarely delivered in a vacuum. Analyze the attack vector:
# 1. Did it come via an urgent WhatsApp/Signal message?
# 2. Is the caller ID spoofed? (Check telecom routing logs if available)
# 3. Did the deepfake video call happen over Zoom/Teams with a "broken camera" excuse?
# 4. Analyze email headers if sent via email
```

## 🔵 Blue Team Detection & Defense
- **Liveness Checks**: Require users to turn their head side-to-side or pass hands over their face during live video verification (breaks facial tracking).
- **Challenge-Response**: During suspected voice clones, ask a question only the real person would know (that isn't public on social media).
- **Watermarking**: Implement invisible watermarking for internal corporate media to establish baseline provenance.
- **Verification Protocols**: Implement strict callbacks for any financial requests, regardless of who appears to be calling.

## Key Concepts
| Concept | Description |
|---------|-------------|
| Deepfake | Synthetic media where a person in existing image/video is replaced by someone else |
| Voice Cloning | Synthesizing a person's voice from a short audio sample |
| C2PA | Open technical standard providing publishers/creators a way to opt-in to tracing origin |
| Spectral Analysis | Analyzing the frequencies of an image/audio to find synthetic generation artifacts |
| Vishing | Voice phishing, increasingly augmented with real-time AI voice changers |

## Output Format
```
Synthetic Media Analysis Report
===============================
Subject: Urgent Wire Transfer Voicemail (CEO Impersonation)
Date of Analysis: 2024-X-X
Conclusion: HIGH PROBABILITY SYNTHETIC AUDIO (Voice Clone)

Artifacts Detected:
1. Spectrogram Analysis: Hard frequency cutoff at 11kHz, typical of ElevenLabs generation.
2. Acoustic Anomalies: Complete absence of inhalation/breathing sounds over a 45-second clip.
3. Metadata: Audio file stripped of all recording device metadata, encoded via standard FFmpeg without hardware signatures.
4. Delivery Vector: Received via VoIP number matching known spoofing patterns, not the CEO's registered mobile device.

Recommendation: DO NOT process the wire transfer. Initiate internal incident response for targeted social engineering.
```

## 🛡️ Remediation & Mitigation Strategy
- **Input Validation:** Sanitize and strictly type-check all inputs.
- **Least Privilege:** Constrain component execution bounds.


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- MITRE ATLAS: [AML.T0048 - Synthetic Media](https://atlas.mitre.org/techniques/AML.T0048/)
- Deepware Scanner: [Deepware](https://deepware.ai/)
- Reality Defender: [Reality Defender](https://www.realitydefender.com/)
