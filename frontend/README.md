# PixelGhost Frontend (React + Vite)

Modern frontend for the PixelGhost FastAPI backend.

## Stack

- React + TypeScript (Vite)
- Tailwind CSS
- shadcn/ui component patterns
- TanStack Query for server state
- Axios API client
- OpenAPI-generated TypeScript schema (`openapi-typescript`)

## Setup

```bash
cp .env.example .env
npm install
npm run dev
```

Default app URL: `http://localhost:5173`

## Type generation

OpenAPI schema is committed as `openapi.json`.

```bash
npm run generate:types
```

This regenerates `src/lib/api/schema.ts` from `openapi.json`.

## Build

```bash
npm run build
npm run preview
```
