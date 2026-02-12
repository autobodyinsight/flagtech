# Data Flow Verification - Render Database Flow

## Overview
All FlagTech data is now persisted to Render PostgreSQL database and follows a complete multi-tenant domain-aware flow.

## Critical Data Flow Components

### 1. ESTIMATE UPLOAD & SAVE FLOW
✅ **Upload endpoint**: `/ui/estimate` or `/ui/grid`
- Parses PDF and extracts repair data
- Saves to `saved_estimates` table with domain
- Captures: vehicle info, labor/paint/parts repairs, owner info, insurance data, VIN, claim#

✅ **Save endpoint**: `/api/estimate-save` (POST)
- Called from UI modal after user reviews estimate
- Saves complete estimate with all fields including **domain** (mandatory)
- Stores in `saved_estimates` table in Render

### 2. TECH MANAGEMENT FLOW  
✅ **Add Tech endpoint**: `/api/techs/add` (POST)
- Creates technician record
- Captures: first_name, last_name, pay_rate, **domain** (mandatory)
- Saves to `techs` table in Render

✅ **List Techs endpoint**: `/api/techs/list` (GET)
- Retrieves **only** techs for authenticated user's domain
- Returns active technicians filtered by domain

✅ **Delete Tech endpoint**: `/api/techs/delete` (POST)
- Soft deletes technician (sets active=false)
- Only affects techs in user's domain

### 3. TECH ASSIGNMENT FLOW
✅ **Save Assignment endpoint**: `/api/ro-assignments` (POST)
- Assigns tech to RO repairs (labor or paint)
- Input: ro, role (labor/paint), tech_id, tech_name, excluded_lines
- Calculates assigned_hours based on line exclusions
- Saves to `ro_assignments` table with **domain**

✅ **Get Assignments endpoint**: `/api/ro-repairs` (GET)
- Retrieves repair lines and existing assignments for RO
- Filters by domain
- Returns: labor_repairs, paint_repairs, assignments

✅ **Tech Assignments endpoint**: `/api/tech-assignments` (GET)
- Lists all ROs assigned to a specific tech
- Filters by domain and tech_id
- Returns: ro, role, total_hours, excluded_lines

### 4. DASHBOARD DATA AGGREGATION
✅ **Dashboard Data endpoint**: `/api/dashboard-data` (GET)
- Retrieves all estimates for user's domain
- Retrieves all tech assignments for user's domain
- Aggregates:
  - **Total Hours Per Tech**: Sum of assigned hours (labor + paint)
  - **Total ROs Per Tech**: Count of unique ROs per tech
  - **Average Hours**: Total hours / RO count
  - **Average RO Value**: Total sales / RO count
  - **RO List**: All ROs with current assignments

### 5. PHASE BOARD TRACKING
✅ **Phase Update endpoint**: `/api/phase/update` (POST)
- Tracks RO phases (draft, review, complete, etc.)
- Saves to `ro_phases` table with domain

✅ **Phase Board endpoint**: `/api/phase/board` (GET)
- Retrieves phase status for all ROs in domain

## Database Schema - Render PostgreSQL

### Table: saved_estimates
```
id (PK)
ro (VARCHAR)
vehicle, year, make, model (TEXT/VARCHAR)
owner_info, insurance_company, claim_number, vin (TEXT)
labor_repairs, paint_repairs, parts_repairs (JSONB)
estimate_totals, parts_total, grand_total, deductible (NUMERIC)
customer_pay, insurance_pay (NUMERIC)
phone_original, phone_override (TEXT)
domain (VARCHAR) - REQUIRED for multi-tenancy
saved_at (TIMESTAMP)
Index: (ro, domain)
```

### Table: techs
```
id (PK)
first_name, last_name (VARCHAR)
pay_rate (NUMERIC)
domain (VARCHAR) - REQUIRED for multi-tenancy
active (BOOLEAN)
created_at (TIMESTAMP)
Index: (domain, active)
```

### Table: ro_assignments
```
id (PK)
ro (VARCHAR)
role (VARCHAR - 'labor' or 'paint')
tech_id (INTEGER, FK -> techs)
tech_name (VARCHAR)
excluded_lines (JSONB - array of line keys)
assigned_hours (NUMERIC)
domain (VARCHAR) - REQUIRED for multi-tenancy
updated_at (TIMESTAMP)
Unique Index: (ro, role, domain)
```

### Table: ro_phases
```
id (PK)
ro (VARCHAR)
phase (VARCHAR - status)
domain (VARCHAR) - REQUIRED for multi-tenancy
updated_at (TIMESTAMP)
Unique Index: (ro, domain)
```

### Table: ro_notes
```
id (PK)
ro (VARCHAR)
note (TEXT)
domain (VARCHAR) - REQUIRED for multi-tenancy
created_at (TIMESTAMP)
Index: (ro, domain)
```

## Multi-Tenancy & Domain Filtering

All queries follow this pattern:
```sql
WHERE domain = %s AND [other conditions]
```

Domain is retrieved from:
```python
from app.services.middleware import get_user_domain
domain = get_user_domain(request)
```

This ensures complete data isolation between companies.

## Data Retention & Future Retrieval

✅ **Persistent Storage**: All data saved to Render PostgreSQL
✅ **Domain-Based Queries**: Only retrieve your company's data
✅ **Historical Data**: All saved estimates retained indefinitely
✅ **Tech Assignments**: All assignments retained and retrievable
✅ **Dashboard Reports**: Pull from persisted database on demand

## End-to-End Flow Example

```
1. User uploads PDF estimate
   → Parsed and displayed in UI
   → User clicks Save
   → Data saved to saved_estimates (domain: user's domain)

2. User goes to HRS (Techs screen)
   → GET /api/techs/list → Returns user's techs (filtered by domain)
   → User creates new tech
   → POST /api/techs/add → Saves with user's domain

3. User goes to Dashboard
   → Clicks HRS column on RO line
   → Modal opens for tech assignment
   → Selects tech and lines to exclude
   → POST /api/ro-assignments → Saves assignment (domain: user's domain)
   → GET /api/dashboard-data → Recalculates metrics for user's domain

4. Dashboard displays:
   → Total Hours Per Tech (aggregated from ro_assignments)
   → Total ROs Per Tech (count unique ROs per tech)
   → RO list with assigned techs

5. Next session:
   → User logs in with same domain
   → Dashboard loads all persisted data
   → Techs list shows all saved technicians
   → All previous assignments visible and editable
```

## Critical Implementation Details

✅ All saves include domain parameter
✅ All retrieves filter by domain
✅ Domain from get_user_domain(request)
✅ Render PostgreSQL connection established at startup
✅ Autocommit enabled for consistency
✅ Proper error handling for auth failures
✅ Null/missing domain treated as unauthorized

## Verification Checklist

- [x] Estimates save with domain to Render
- [x] Techs saved with domain to Render
- [x] Tech assignments saved with domain to Render  
- [x] Dashboard queries filtered by domain
- [x] Phase tracking includes domain
- [x] Notes include domain
- [x] All retrieval queries have WHERE domain = %s
- [x] Multi-user isolation confirmed
- [x] Data persistence across sessions confirmed
- [x] Future retrieval from Render confirmed
