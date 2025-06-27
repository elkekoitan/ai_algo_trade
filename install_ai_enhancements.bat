@echo off
echo 🚀 Installing AI Enhancements for ai_algo_trade
echo ===============================================
echo.

echo 📦 Installing Frontend Dependencies...
cd frontend
call npm install @tensorflow/tfjs @tensorflow/tfjs-react-native @tensorflow/tfjs-node three @types/three d3 @types/d3 ml-matrix chartjs-adapter-date-fns react-speech-recognition react-webcam tone
echo.

echo 🐍 Installing Backend Dependencies...
cd ..\backend
pip install tensorflow==2.15.0 torch==2.1.2 scikit-learn==1.3.2 yfinance==0.2.28 newsapi-python==0.2.7 textblob==0.17.1 transformers==4.36.2 opencv-python==4.8.1.78 Pillow==10.1.0 matplotlib==3.8.2 seaborn==0.13.0 plotly==5.17.0 lightgbm==4.1.0 xgboost==2.0.2 catboost==1.2.2 optuna==3.5.0 hyperopt==0.2.7 mlflow==2.9.2 wandb==0.16.1 kafka-python==2.0.2 celery==5.3.4 dask==2023.12.1 joblib==1.3.2
echo.

echo ✅ Installation Complete!
echo.
echo 🎯 AI Enhancements Added:
echo   ✓ TensorFlow.js for real-time ML
echo   ✓ Advanced pattern recognition
echo   ✓ Neural network visualization
echo   ✓ AI-powered predictions
echo   ✓ Sentiment analysis
echo   ✓ Computer vision for charts
echo.
echo 🚀 Start the enhanced platform:
echo   Backend: cd backend ^&^& python main.py
echo   Frontend: cd frontend ^&^& npm run dev
echo.
echo 📊 New AI Endpoints Available:
echo   • http://localhost:8001/api/v1/ai/pattern-analysis
echo   • http://localhost:8001/api/v1/ai/models/status
echo   • http://localhost:8001/api/v1/ai/neural-activity
echo   • http://localhost:8001/api/v1/ai/predictions
echo   • http://localhost:8001/api/v1/ai/sentiment
echo.
echo 💫 Access Quantum AI Dashboard: http://localhost:3000/quantum
echo.
cd ..
pause 