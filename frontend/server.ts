import express from 'express';
import cors from 'cors';
import multer from 'multer';
import { createServer as createViteServer } from 'vite';
// import { calculateEMI } from './src/backend/services/emiCalculator';
// import { analyzeBankStatement } from './src/backend/services/bankAnalyzer';
// import { predictLoanRisk } from './src/backend/services/mlEngine';
// import { generateCreditScore } from './src/backend/services/creditScore';

const upload = multer({ storage: multer.memoryStorage() });

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(cors());
  app.use(express.json());

  // --- API ROUTES ---

  // app.post('/api/auth/login', (req, res) => {
  //   const { email, password } = req.body;
  //   // Mock authentication
  //   if (email && password) {
  //     res.json({ token: 'mock-jwt-token', user: { email, role: 'loan_officer' } });
  //   } else {
  //     res.status(401).json({ error: 'Invalid credentials' });
  //   }
  // });

  // app.post('/api/upload/bank-statement', upload.single('file'), (req, res) => {
  //   if (!req.file) {
  //     return res.status(400).json({ error: 'No file uploaded' });
  //   }
  //
  //   // Simulate parsing the file
  //   const analysis = analyzeBankStatement(req.file.buffer, req.file.originalname);
  //   res.json(analysis);
  // });

  // app.post('/api/loan/calculate-emi', (req, res) => {
  //   const { loanAmount, interestRate, durationMonths } = req.body;
  //   if (!loanAmount || !interestRate || !durationMonths) {
  //     return res.status(400).json({ error: 'Missing required fields' });
  //   }
  //
  //   const result = calculateEMI(loanAmount, interestRate, durationMonths);
  //   res.json(result);
  // });

  // app.post('/api/loan/predict', (req, res) => {
  //   const applicationData = req.body;
  //
  //   // 1. Generate Credit Score
  //   const creditScore = generateCreditScore(applicationData);
  //
  //   // 2. Run ML Model Prediction
  //   const prediction = predictLoanRisk({ ...applicationData, creditScore });
  //
  //   // 3. Save to mock database (in-memory for now)
  //   const applicationRecord = {
  //     id: Math.random().toString(36).substring(7),
  //     studentId: 'student_123',
  //     ...applicationData,
  //     creditScore,
  //     ...prediction,
  //     createdAt: new Date().toISOString()
  //   };

  //   mockDatabase.applications.push(applicationRecord);
  //
  //   res.json(applicationRecord);
  // });

  // app.get('/api/dashboard/metrics', (req, res) => {
  //   // Mock student specific data
  //   const myApplications = mockDatabase.applications.filter(app => app.studentId === 'student_123');
  //   const activeLoan = myApplications.find(app => app.decision === 'Approved');
  //
  //   res.json({
  //     totalBorrowed: activeLoan ? `$${activeLoan.loanAmount.toLocaleString()}` : '$0',
  //     nextPayment: activeLoan ? '$215.00' : '-',
  //     creditScore: '720',
  //     recentStatus: myApplications.length > 0 ? myApplications[myApplications.length - 1].decision : 'No Applications',
  //     myApplications: myApplications.reverse()
  //   });
  // });

  // --- VITE MIDDLEWARE ---
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static('dist'));
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

// Mock Database
// const mockDatabase = {
//   applications: [
//     {
//       id: 'app_1',
//       studentId: 'student_123',
//       applicantName: 'Jane Doe',
//       loanAmount: 5000,
//       loanPurpose: 'Tuition Fees',
//       decision: 'Approved',
//       riskScore: 0.15,
//       createdAt: new Date(Date.now() - 86400000).toISOString()
//     }
//   ] as any[]
// };

startServer();
