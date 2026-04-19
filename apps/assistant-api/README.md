# assistant-api

FastAPI service for Ash Assistant.

## Purpose

This service is the backend entry point for the assistant. It currently provides a health endpoint and the base wiring for configuration, logging, routing, middleware, providers, and orchestration services.

## Run Locally

```powershell
Set-Location c:\Ashu\Project-Ash\apps\assistant-api
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## API

- `GET /api/v1/health` returns a simple service status payload.

## Current Structure

- `app/main.py` - FastAPI application entry point
- `app/core` - configuration and logging helpers
- `app/api/v1` - HTTP routing and endpoints
- `app/providers` - model integration abstractions
- `app/services` - orchestration logic
- `app/middleware` - app-wide handlers
- `app/schemas` - shared request and response models

## Dependencies

Install the root `requirements.txt` from the repository root before running the service.