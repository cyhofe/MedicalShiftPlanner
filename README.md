# MedicalShiftPlanner

## Overview
A Streamlit-based app for booking flexible medical staff: location managers place requests, and a central coordinator approves, reschedules, or cancels.

## Architecture
- **Frontend:** Streamlit (Python)
- **ORM:** SQLAlchemy (Users, Locations, Workers, Bookings)
- **Auth:** bcrypt-hashed passwords + JWT
- **Email:** SendGrid or SMTP
- **Database:** SQLite (dev) / PostgreSQL (prod)

## Local Setup
