# ──────[ PixelGhost | ∆H ]──────

**PixelGhost** is an open-source, high-performance image steganography engine built for scale and modularity. Designed with cryptographic integrity and future agentic integration in mind, PixelGhost lets you embed, extract, and audit data in images using classic and cutting-edge techniques.

## 🚀 Features

- 🔍 **Modular Steganography Engine** (LSB, DCT, DFT, DWT coming soon)
- 🔐 Privacy-first: future support for homomorphic transformations
- 🧱 FastAPI backend with CI/CD pipeline and Docker support
- ⚛️ **Modern React Frontend** (Vite, TypeScript, Tailwind, Shadcn/UI, TanStack Query)
- 🔗 API-first design

## 🧩 Use Cases

- Secure image watermarking
- Embedding metadata/personality into images
- Obfuscated communication tools
- Educational cryptography

## 🛠️ Getting Started

### Run with Docker

1. Ensure you have Docker and Docker Compose installed.
2. Clone this repository.
3. Run:
   ```bash
   docker compose up --build
   ```
4. Access the **Frontend** at `http://localhost:5173`
5. Access the **API Docs** at `http://localhost:8000/docs`

### Manual Run

#### Backend (FastAPI)
1. Create a virtual environment: `python -m venv .venv`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

#### Frontend (React)
1. Install dependencies: `npm install` inside `frontend/`
2. Run development server: `npm run dev`
3. Access at `http://localhost:5173`
