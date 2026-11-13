# HeartXAI: Review-II Project Presentation Record (Semester-I)

**Document ID:** HXAI-REF-001  
**Project:** HeartXAI: Explainable AI-Based Cardiovascular Risk Prediction and Personalized Medical Assistance System  
**Review Stage:** Review-II (Semester-I)  
**Date of Presentation:** 12-11-2026  
**Institution:** Anil Neerukonda Institute of Technology & Sciences (Autonomous), Department of Information Technology  
**Project Guide:** Mr. N. Chaitanya Kumar, Assistant Professor, Department of Information Technology  
**Student Team (Team 13):**  
- Karri Vijay Rama Reddy (A23126511083)  
- Pudi Hemanth (A23126511110)  
- Edhubilli Sandeep Kumar (A23126511197)  
- Nimmakayala Goutham Sagar (A23126511098)  

---

## 1. Abstract & Problem Identification

### Abstract
Cardiovascular diseases are a major cause of health-related complications worldwide, making early risk assessment and proper healthcare guidance important. This project proposes HeartXAI, an Explainable Artificial Intelligence (XAI)-based system designed to predict cardiovascular risk and provide personalized medical assistance. The system uses Machine Learning algorithms to analyze patient health parameters available in a validated dataset and classify the predicted risk into Low, Medium and High categories. Explainable AI techniques, particularly SHAP (SHapley Additive Explanations), are used to identify the major factors influencing individual predictions. Counterfactual analysis is incorporated to demonstrate how hypothetical changes in modifiable health parameters may influence the predicted risk. Based on the assessment, the system provides general diet, exercise and lifestyle recommendations. It also offers doctor consultation assistance by displaying nearby cardiologists, hospital details and contact information. Additionally, a health insurance assistance module helps users explore and compare available policies based on coverage, premiums, waiting periods and exclusions. The expected outcome is an integrated web-based system that combines cardiovascular risk prediction, explainability and medical assistance to support health awareness and informed decision-making. The system is intended for awareness and does not replace professional medical diagnosis or treatment.

### Problem Statement & Research Gap
1. **Problem Statement:** Early identification of cardiovascular risk is important. Traditional ML models may not clearly explain their predictions. Patients need understandable risk explanations and guidance.
2. **Existing System:** The IEEE 2025 base paper studies heart disease prediction and risk stratification using XAI techniques (SHAP, LIME, Grad-CAM, LRP, PDP).
3. **Research Gap:** Lack of an integrated patient-facing assistance platform. Limited integration of prediction with lifestyle guidance, doctor consultation, and insurance information.
4. **Proposed Solution:** HeartXAI combines ML-based risk prediction, SHAP explanations, counterfactual analysis, and personalized medical assistance.
5. **Core Objectives:**
   - Predict cardiovascular risk using ML.
   - Explain predictions using SHAP.
   - Perform counterfactual analysis.
   - Provide diet and lifestyle guidance.
   - Assist with doctor search and health insurance information.

---

## 2. System Design & Architectural Specifications

### 2.1 System Architecture Flow
```
Patient
  │
  ▼
HeartXAI Web Application
  │
  ▼
Registration / Login
  │
  ▼
Health Parameter Input
  │
  ▼
Data Validation & Preprocessing
  │
  ▼
Machine Learning Model
  │
  ▼
Cardiovascular Risk Prediction
  ├──► SHAP Explanation ───────────────┐
  └──► Counterfactual Analysis ────────┤
                                       ▼
                               Patient Dashboard
                                       │
     ┌───────────────────┬─────────────┴───────┬────────────────────────┐
     ▼                   ▼                     ▼                        ▼
Diet & Lifestyle   Doctor Consultation   Health Insurance        Health Assessment
   Guidance            Assistance           Information               History
```

### 2.2 Use Case Specification
- **Patient Use Cases:**
  - Register & Login
  - Enter Health Parameters
  - View Cardiovascular Risk Prediction
  - View SHAP Explanation
  - Perform Counterfactual Analysis
  - View Diet and Lifestyle Guidance
  - Search Nearby Doctors and Hospitals & View Doctor Details
  - Explore Health Insurance Policies & Compare Insurance Policies
  - View Assessment History
- **Admin Use Cases:**
  - Admin Login & Access Admin Dashboard
  - Add, Update, Delete Doctor Profile
  - Manage Hospital Information
  - Add, Update, Delete Insurance Policy & Manage Insurance Details

### 2.3 Activity Diagram Specification
- **Patient Swimlane:** Open Application $\rightarrow$ Register/Login $\rightarrow$ Enter Health Parameters $\rightarrow$ Submit $\rightarrow$ View Risk Prediction $\rightarrow$ Optional: View SHAP / View Counterfactual $\rightarrow$ View Medical Assistance $\rightarrow$ Optional: Search Doctor/Hospital $\rightarrow$ Optional: Explore Insurance $\rightarrow$ View Assessment History.
- **HeartXAI System Swimlane:** Validate Login $\rightarrow$ Receive Health Parameters $\rightarrow$ Preprocess Data $\rightarrow$ Apply ML Model $\rightarrow$ Generate Prediction $\rightarrow$ Generate SHAP Explanation $\rightarrow$ Perform Counterfactual Analysis $\rightarrow$ Generate Lifestyle Guidance $\rightarrow$ Retrieve Doctor/Hospital Information $\rightarrow$ Retrieve Insurance Information $\rightarrow$ Save Assessment History $\rightarrow$ Display Results.
- **Admin Swimlane:** Admin Login $\rightarrow$ Access Admin Dashboard $\rightarrow$ Branch by Action: (1) Manage Doctor Profiles (Add/Update/Delete), (2) Manage Hospital Information, (3) Manage Insurance Policies (Add/Update/Delete) $\rightarrow$ Save Updated Info to Database $\rightarrow$ End.

### 2.4 Class Diagram Specification
- **`Patient`:** `patientId`, `name`, `age`, `email`, `password`; `register()`, `login()`, `enterHealthData()`, `viewResults()`.
- **`MLModel`:** `modelName`, `algorithm`, `version`; `preprocessData()`, `predictRisk()`.
- **`Prediction`:** `predictionId`, `riskLevel`, `probability`, `date`; `getRiskLevel()`, `getProbability()`.
- **`Explanation`:** `explanationId`, `importantFactors`, `shapValues`; `generateSHAPExplanation()`, `getInsights()`.
- **`CounterfactualAnalysis`:** `analysisId`, `originalRisk`, `suggestedChanges`, `newRisk`; `generateCounterfactual()`, `compareRisk()`.
- **`MedicalAssistance`:** `assistanceId`, `dietPlan`, `exerciseTips`, `lifestyleGuidance`; `getDietPlan()`, `getExerciseTips()`.
- **`DoctorConsultation`:** `doctorId`, `doctorName`, `specialization`, `hospitalName`, `contactNumber`, `location`; `addDoctor()`, `updateDoctor()`, `deleteDoctor()`, `searchDoctors()`, `viewDoctorDetails()`.
- **`HealthInsurance`:** `insuranceId`, `providerName`, `policyName`, `coverage`, `premium`, `waitingPeriod`, `exclusions`; `addPolicy()`, `updatePolicy()`, `deletePolicy()`, `viewPolicies()`, `comparePolicies()`.
- **`AssessmentHistory`:** `historyId`, `predictionDate`, `riskLevel`, `notes`; `saveRecord()`, `getHistory()`.
- **`Admin`:** `adminId`, `name`, `email`, `password`; `login()`, `accessDashboard()`, `manageDoctors()`, `manageInsurance()`.

### 2.5 Sequence Diagram Specification
- **Part 1 (Patient Workflow):** Patient $\rightarrow$ Web App $\rightarrow$ ML Model (Preprocess & Predict) $\rightarrow$ SHAP Module (Request Explanation & Insights) $\rightarrow$ Medical Module (Request Advice & Provider List) $\rightarrow$ Web App $\rightarrow$ Patient.
- **Part 2 (Admin Workflow):** Admin $\rightarrow$ Dashboard $\rightarrow$ Management Modules $\rightarrow$ Database (Create/Update Doctor Record, Create/Update Insurance Policy).

### 2.6 Component Diagram Specification
- **Presentation Layer:** Patient Interface, Admin Interface.
- **Application Layer:** Backend Controller, Data Processing, Medical Assistance.
- **AI and Analytics Layer:** Machine Learning, SHAP Explanation, Counterfactual Analysis.
- **Data Layer:** Database Component.

---

## 3. Algorithms & Technical Approach

### Algorithms Evaluated
1. **Logistic Regression (Baseline Model):** Simple, interpretable probability prediction.
2. **Random Forest (Robust Ensemble):** Multiple decision trees reducing variance and overfitting.
3. **XGBoost (Advanced Boosting Algorithm):** Sequential tree error correction for state-of-the-art accuracy.

### Algorithm Selection Protocol
- Train all three algorithms using the heart disease dataset.
- Compare using accuracy, precision, recall, and F1-score.
- Deploy the most suitable model.

### Explainable AI & Counterfactual Approach
- **SHAP (SHapley Additive exPlanations):** Computes feature-level contribution scores indicating whether each parameter increases or decreases predicted risk; visual plots for transparency.
- **Counterfactual Analysis:** Identifies hypothetical changes in modifiable parameters (e.g. lowering cholesterol or blood pressure) and shows resulting change in risk.

---

## 4. Academic References Cited
1. *"Comprehensive Study on Heart Disease Prediction and Risk Stratification using Explainable Artificial Intelligence Technique,"* IEEE, 2025.
2. S. M. Lundberg and S. I. Lee, *"A Unified Approach to Interpreting Model Predictions,"* Advances in Neural Information Processing Systems (NeurIPS), 2017.
3. S. Wachter, B. Mittelstadt and C. Russell, *"Counterfactual Explanations Without Opening the Black Box,"* Harvard Journal of Law & Technology, 31(2):841–887, 2018.
