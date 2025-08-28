# 📱 QR Code Attendance System

A simple, free QR code-based attendance system that works on Railway without external costs.

## ✨ Features

- **QR Code Generation** - Generate unique QR codes for each class session
- **Mobile-Friendly Forms** - Students scan QR codes and fill forms on their phones
- **One-Time Use Tokens** - Each QR code can only be used once
- **Duplicate Prevention** - Prevents multiple attendance marks per student per day
- **CSV Export** - Download attendance records after each class
- **Admin Panel** - View attendance counts and manage records
- **No External Costs** - Works completely free on Railway

## 🚀 Quick Start

### 1. **Generate QR Code**
- Visit your app: `https://your-app.railway.app/`
- Click "Generate New QR Code" button
- Display the QR code for students to scan

### 2. **Students Mark Attendance**
- Students scan QR code with their phone camera
- Form automatically opens with pre-filled token
- Students enter: First Name, Last Name, Student ID
- Form submits and closes automatically

### 3. **Download Attendance**
- After class, visit: `https://your-app.railway.app/admin`
- Click "Download CSV" to get attendance records
- Click "Clear All Records" to reset for next class

## 📱 How It Works

1. **Teacher generates QR code** → Students scan with phones
2. **QR code opens form** → Students fill details and submit
3. **Attendance saved** → Form closes to prevent reuse
4. **Download CSV** → Get attendance records after class
5. **Clear records** → Reset for next session

## 🔧 Technical Details

- **Framework**: Flask (Python)
- **Storage**: In-memory (persists during Railway session)
- **Deployment**: Railway (free tier)
- **No Database**: Simple, lightweight solution
- **No External APIs**: Completely self-contained

## 🌐 URLs

- **Main Page**: `/` - Generate QR codes
- **Student Form**: `/submit/<token>` - Mobile attendance form
- **Admin Panel**: `/admin` - View and manage attendance
- **CSV Download**: `/attendance.csv` - Download attendance data
- **API Endpoints**: Various endpoints for form submission and management

## 💡 Benefits

✅ **Completely Free** - No Google Cloud charges  
✅ **Works on Railway** - No file system issues  
✅ **Real-time Updates** - See attendance as it happens  
✅ **Mobile Optimized** - Perfect for student phones  
✅ **Simple Management** - Easy CSV download and clearing  
✅ **Secure** - One-time use tokens, duplicate prevention  

## 🎯 Perfect For

- **Classroom attendance**
- **Workshop check-ins**
- **Event registrations**
- **Meeting attendance**
- **Any quick data collection**

## 📊 After Each Class

1. **Download CSV**: Get attendance records
2. **Clear Records**: Reset for next session
3. **Save CSV**: Store in your preferred location
4. **Repeat**: Generate new QR code for next class

This system gives you the convenience of digital attendance without any ongoing costs or complexity!
