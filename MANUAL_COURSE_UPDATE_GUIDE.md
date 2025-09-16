# Manual Course Update Guide

## Overview
This guide will help you manually update your AgriQuest system with proper BS Agriculture courses through the admin interface.

## Prerequisites
- Your Render app must be running and accessible
- You must have admin access (username: `admin`, password: `admin123`)

## Step-by-Step Instructions

### 1. Access Your App
1. Go to your Render app URL (e.g., `https://your-app-name.onrender.com`)
2. Login with admin credentials:
   - Username: `admin`
   - Password: `admin123`

### 2. Navigate to Admin Dashboard
1. After login, you should be redirected to the admin dashboard
2. Look for "Manage Subjects" or "Subjects" section

### 3. Remove Existing Subjects
1. Go to the subjects management page
2. Delete all existing subjects one by one
3. This ensures a clean slate for the new agriculture courses

### 4. Add New BS Agriculture Subjects

#### Year 1 - Introductory Agriculture Courses

**Subject 1: Introduction to Agriculture**
- Name: `Introduction to Agriculture`
- Description: `Overview of agriculture, its importance, and basic concepts in agricultural science.`
- Year: `1`
- Code: `AGRI-101`

**Subject 2: Fundamentals of Crop Science I**
- Name: `Fundamentals of Crop Science I`
- Description: `Basic principles of crop production, plant growth, and development.`
- Year: `1`
- Code: `AGRI-102`

**Subject 3: Fundamentals of Soil Science I**
- Name: `Fundamentals of Soil Science I`
- Description: `Introduction to soil properties, composition, and basic soil management.`
- Year: `1`
- Code: `AGRI-103`

**Subject 4: Introduction to Animal Science**
- Name: `Introduction to Animal Science`
- Description: `Basic concepts of animal production, nutrition, and husbandry.`
- Year: `1`
- Code: `AGRI-104`

#### Year 2 - Core Agriculture Courses

**Subject 5: Fundamentals of Crop Science II**
- Name: `Fundamentals of Crop Science II`
- Description: `Advanced crop production techniques, breeding, and biotechnology.`
- Year: `2`
- Code: `AGRI-201`

**Subject 6: Soil Science II**
- Name: `Soil Science II`
- Description: `Advanced soil chemistry, fertility, and sustainable soil management.`
- Year: `2`
- Code: `AGRI-202`

**Subject 7: Animal Science II**
- Name: `Animal Science II`
- Description: `Advanced animal nutrition, breeding, and production systems.`
- Year: `2`
- Code: `AGRI-203`

**Subject 8: General Entomology**
- Name: `General Entomology`
- Description: `Study of insects, their role in agriculture, and pest management.`
- Year: `2`
- Code: `AGRI-204`

**Subject 9: Plant Pathology (Intro)**
- Name: `Plant Pathology (Intro)`
- Description: `Introduction to plant diseases, their causes, and management strategies.`
- Year: `2`
- Code: `AGRI-205`

**Subject 10: Agricultural Extension & Communication (Intro)**
- Name: `Agricultural Extension & Communication (Intro)`
- Description: `Principles of agricultural extension, communication, and rural development.`
- Year: `2`
- Code: `AGRI-206`

### 5. Create Sample Quizzes (Optional)
For each subject, you can create sample quizzes:

1. Go to the quiz management section
2. Create a quiz for each subject with:
   - Title: `[Subject Name] - Quiz 1`
   - Description: `Basic quiz for [Subject Name]`
   - Add 2-3 sample questions with multiple choice answers

### 6. Assign Teachers to Subjects
1. Go to teacher management
2. Assign existing teachers to the new subjects
3. Ensure each subject has at least one teacher assigned

## Verification
After completing the update:

1. **Check Subjects**: Verify all 10 subjects are created and properly categorized by year
2. **Test Login**: Try logging in as different user types (admin, teacher, student)
3. **Check Dashboards**: Ensure all dashboards show the new subjects correctly
4. **Test Quizzes**: If you created quizzes, test taking them as a student

## Troubleshooting

### If you can't access the admin interface:
- Check if your Render app is running (not showing 502 errors)
- Verify the admin credentials are correct
- Check if the app URL is correct

### If subjects don't appear:
- Refresh the page
- Check if the database connection is working
- Verify the subjects were saved properly

### If you need to start over:
- Delete all subjects and recreate them
- Make sure to use the exact names and codes provided above

## Summary
After completing this update, your AgriQuest system will have:
- ✅ 10 proper BS Agriculture subjects
- ✅ Subjects organized by year (1st and 2nd year)
- ✅ Proper subject codes (AGRI-101 to AGRI-206)
- ✅ Comprehensive descriptions for each subject
- ✅ Clean, organized curriculum structure

This will provide a solid foundation for your agriculture education platform!
