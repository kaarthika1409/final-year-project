import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed_data import seed_nutrition_database
from backend.app.routers import auth, meals, targets, recommendations, analytics
from backend.app.routers import predict as predict_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nutrition_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables and seed nutrition reference dataset
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Seeding nutrition reference database...")
        seed_nutrition_database(db)
    finally:
        db.close()

    yield
    # Shutdown logic if needed


app = FastAPI(
    title="Personalized Nutritional Prediction & Adaptive Dietary Recommendation System",
    description=(
        "FastAPI Backend providing JWT Authentication, Mifflin-St Jeor BMR Calorie Budgeting, "
        "Manual & ML Photo Food Logging, Adaptive Meal Slot Redistribution, "
        "Macro & Preference-based Recommendation Engine, and Demographic Accuracy Evaluation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration for Vite React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(meals.router)
app.include_router(targets.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(predict_router.router)


@app.get("/")
def root():
    return {
        "status": "online",
        "system": "Personalized Nutritional Prediction & Adaptive Dietary Recommendation System",
        "documentation": "/docs",
        "version": "1.0.0",
    }
