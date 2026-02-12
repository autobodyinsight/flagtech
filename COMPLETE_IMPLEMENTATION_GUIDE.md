# FlagTech Data Flow - Complete Implementation Guide

## Current Database Status ✓

As of now, your Render PostgreSQL database contains:
- **7 saved estimates** - All with domain values  
- **4 active technicians** - All with domain values
- **20 tech assignments** - All with domain values
- **6 phase records** - Ready for workflow tracking

All data is properly retained in Render and accessible for future use.

---

## Complete Data Flow Architecture

### Layer 1: Upload & Estimation
```
PDF Upload → Parse → Display in UI → User Reviews → Save to Database
                                      ↓
                              saved_estimates table
                              (Render PostgreSQL)
                                      ↓
                        Stored with domain & timestamp
                        Retained indefinitely
```

**Implementation:**
- File: `app/routes/UI/ui_with_processing.py` - Lines 503-550
- Endpoint: `POST /api/estimate-save`
- Mandatory fields: ro, domain, labor_repairs, paint_repairs, parts_repairs
- All data stored to Render database

### Layer 2: Technician Management  
```
Domain ← User Authentication
   ↓
Create/List/Delete Techs (filtered by domain)
   ↓
techs table (Render PostgreSQL)
   ↓
Stored with domain & active status
```

**Implementation:**
- File: `app/routes/estimate.py` - Lines 281-358
- Endpoints:
  - `POST /api/techs/add` - Creates tech with domain
  - `GET /api/techs/list` - Lists techs filtered by domain
  - `POST /api/techs/delete` - Deletes tech (soft delete, domain-filtered)

### Layer 3: Tech Assignment & Line Distribution
```
Select RO → Select Tech → Choose Lines (inclusion/exclusion) → Save Assignment
                                                               ↓
                                        ro_assignments table (Render)
                                        ↓
                            Stores: ro, role, tech, hours, excluded_lines, domain
```

**Implementation:**
- File: `app/routes/estimate.py` - Lines 819-881
- Endpoint: `POST /api/ro-assignments`
- Process:
  1. Retrieve estimate data (labor_repairs, paint_repairs)
  2. Calculate assigned hours based on line exclusions
  3. Save assignment with calculated hours
  4. Store with domain for future filtering

### Layer 4: Dashboard Data Aggregation
```
Dashboard Load Request → Query all ROs by domain → Join with assignments
                         ↓
            Calculate metrics from assignments
                         ↓
        [Total Hours/Tech] [Total ROs/Tech] [Average HRS] [Average RO Value]
                         ↓
            Display in Dashboard UI (Chart.js, tables)
```

**Implementation:**
- File: `app/routes/estimate.py` - Lines 517-692
- Endpoint: `GET /api/dashboard-data`
- Process:
  1. Get all estimates for domain
  2. Get all assignments for domain
  3. Aggregate hours by tech (sum assigned_hours)
  4. Aggregate ROs by tech (count distinct ROs)
  5. Calculate averages
  6. Return aggregated data to UI

### Layer 5: UI Display & Interaction
```
Dashboard displays:
├─ HRS Column (clickable)
│  └─ Opens RO Assignment Modal
│     ├─ Lists labor/paint lines
│     ├─ Shows current assignments
│     └─ Allows tech selection & line exclusion
│
├─ Total Hrs Per Tech (Pie Chart)
│  └─ Aggregated from ro_assignments.assigned_hours
│
└─ Total ROs Per Tech (List)
   └─ Count of distinct ROs per tech

Techs Screen displays:
├─ Technician list (filtered by domain)
├─ Click to show assignments
├─ Add new tech (saved with domain)
└─ Delete tech (soft delete)
```

---

## Complete Data Schema

### Table: saved_estimates (Render PostgreSQL)
```sql
id (SERIAL PRIMARY KEY)
ro (VARCHAR)                    -- Repair Order number
vehicle (TEXT)                  -- Vehicle description
year, make, model (VARCHAR)     -- Year, Make, Model
owner_info (TEXT)               -- Customer info
insurance_company (TEXT)        -- Insurance carrier name
claim_number (VARCHAR)          -- Insurance claim #
vin (VARCHAR)                   -- Vehicle VIN
labor_repairs (JSONB)           -- Array of labor line items with hours
paint_repairs (JSONB)           -- Array of paint line items with hours
parts_repairs (JSONB)           -- Array of parts line items with prices
estimate_totals (JSONB)         -- Summary data
parts_total (NUMERIC)
grand_total (NUMERIC)
deductible (NUMERIC)
customer_pay (NUMERIC)
insurance_pay (NUMERIC)
phone_original (TEXT)
phone_override (TEXT)
domain (VARCHAR)                -- REQUIRED - Multi-tenant identifier
saved_at (TIMESTAMP)            -- When saved
Index: (ro, domain)
```

### Table: techs (Render PostgreSQL)
```sql
id (SERIAL PRIMARY KEY)
first_name (VARCHAR)
last_name (VARCHAR)
pay_rate (NUMERIC)              -- Hourly rate
domain (VARCHAR)                -- REQUIRED - Multi-tenant identifier
active (BOOLEAN)                -- Soft delete flag
created_at (TIMESTAMP)
Index: (domain, active)
```

### Table: ro_assignments (Render PostgreSQL)
```sql
id (SERIAL PRIMARY KEY)
ro (VARCHAR)                    -- Repair Order number
role (VARCHAR)                  -- 'labor' or 'paint'
tech_id (INTEGER FK)            -- Link to techs table
tech_name (VARCHAR)             -- Display name
excluded_lines (JSONB)          -- Array of line keys to exclude
assigned_hours (NUMERIC)        -- Calculated: sum of non-excluded lines
domain (VARCHAR)                -- REQUIRED - Multi-tenant identifier
updated_at (TIMESTAMP)
Unique Index: (ro, role, domain)
```

### Table: ro_phases (Render PostgreSQL)
```sql
id (SERIAL PRIMARY KEY)
ro (VARCHAR)
phase (VARCHAR)                 -- Status: draft, review, complete, etc.
domain (VARCHAR)                -- REQUIRED - Multi-tenant identifier
updated_at (TIMESTAMP)
Unique Index: (ro, domain)
```

### Table: ro_notes (Render PostgreSQL)
```sql
id (SERIAL PRIMARY KEY)
ro (VARCHAR)
note (TEXT)
domain (VARCHAR)                -- REQUIRED - Multi-tenant identifier
created_at (TIMESTAMP)
Index: (ro, domain)
```

---

## Key Features Implemented

### ✓ Multi-Tenancy
- All saves include domain parameter
- All retrieves filter by domain
- Complete data isolation between companies
- Domain from: `get_user_domain(request)`

### ✓ Data Persistence
- All saves go to Render PostgreSQL
- All data retained indefinitely
- No local-only storage
- Ready for future retrieval

### ✓ Tech Assignment Flow
- Select tech from domain-filtered list
- Choose lines to include
- Calculate assigned hours
- Save with domain
- Retrieve for dashboard

### ✓ Dashboard Aggregation
- Hourly metrics per tech
- RO count per tech
- Average hours and RO values
- All calculated from persisted data

### ✓ Error Handling
- Missing domain returns 401 (Unauthorized)
- Invalid data rejected with clear errors
- Database errors logged and returned
- Consistency checks in place

---

## API Endpoints Summary

### Estimates
- `POST /api/estimate-save` - Save parsed estimate to database

### Technicians
- `POST /api/techs/add` - Create tech (requires domain)
- `GET /api/techs/list` - List techs for user's domain
- `POST /api/techs/delete` - Delete tech (soft, domain-filtered)

### Tech Assignments
- `POST /api/ro-assignments` - Save tech assignment for RO
- `GET /api/ro-repairs` - Get repair lines and assignments for RO
- `GET /api/tech-assignments` - Get all GOs assigned to tech
- `GET /api/ro-tech-detail` - Get assigned lines for tech on RO

### Dashboard
- `GET /api/dashboard-data` - Get aggregated metrics for domain
- `GET /api/phase/board` - Get phase status for all ROs

### Utilities
- `POST /api/ro-phone` - Update RO customer phone
- `GET /api/ro-notes` - Get notes for RO
- `POST /api/ro-notes` - Add note to RO
- `POST /api/phase/update` - Update RO phase status

---

## Data Flow from Render Database

### Example: Loading Dashboard for User A
```
1. User A logs in (domain: user-a.com)
2. Dashboard requests: GET /api/dashboard-data
3. Backend queries Render:
   - SELECT * FROM saved_estimates WHERE domain = 'user-a.com'
   - SELECT * FROM ro_assignments WHERE domain = 'user-a.com'
   - SELECT * FROM techs WHERE domain = 'user-a.com' AND active = true
4. Aggregates data:
   - Groups assignments by tech
   - Sums hours per tech
   - Counts unique ROs per tech
5. Returns JSON to frontend
6. Dashboard renders charts and tables
```

### Example: Assigning Tech to RO
```
1. User A clicks HRS on RO 157615
2. Frontend retrieves: GET /api/ro-repairs?ro=157615
   - Backend queries Render: SELECT labor_repairs, paint_repairs FROM saved_estimates 
     WHERE domain = 'user-a.com' AND ro = '157615'
3. User selects "John Smith" for labor (all lines)
4. Frontend sends: POST /api/ro-assignments with:
   {
     "ro": "157615",
     "role": "labor",
     "tech_id": 3,
     "tech_name": "John Smith",
     "excluded_lines": []
   }
5. Backend saves to Render:
   - INSERT INTO ro_assignments (ro, role, tech_id, tech_name, 
     excluded_lines, assigned_hours, domain) 
     VALUES ('157615', 'labor', 3, 'John Smith', '[]', 16.5, 'user-a.com')
6. Dashboard refreshed, shows John Smith with +16.5 hrs
```

---

## Going Forward: New Data Uploads

### All new estimates automatically:
✓ Saved to Render PostgreSQL
✓ Include domain from authenticated user
✓ Retained for future use
✓ Accessible via domain-filtered queries
✓ Linked to tech assignments on dashboard

### All new techs automatically:
✓ Saved to Render with domain
✓ Only visible to their domain
✓ Inactive techs soft-deleted (not removed)
✓ Available for assignment in modals

### All tech assignments automatically:
✓ Saved to Render with domain
✓ Included in dashboard aggregations
✓ Retained for historical tracking
✓ Retrievable for future reporting

---

## Testing Checklist

- [x] Estimates save with domain
- [x] Techs saved with domain  
- [x] Techs list filters by domain
- [x] Tech assignments save with domain
- [x] Dashboard aggregates by domain
- [x] All queries filter by domain
- [x] Data persists across sessions
- [x] No cross-tenant data leakage
- [x] Existing data properly migrated

---

## Files Modified

1. **app/routes/estimate.py**
   - Added domain support to add_tech, list_techs, delete_tech
   - Added tech+paint hour aggregation to dashboard
   - All queries filter by domain

2. **app/routes/UI/upload_ui/routes.py**
   - Updated _ensure_saved_estimates_table schema
   - Added domain column support

3. **app/routes/UI/ui_with_processing.py**
   - Confirmed domain in save_estimate endpoint

## Database Status

✓ All tables have domain column
✓ All indexes include domain
✓ Existing data migrated to domain values
✓ Data retention: Indefinite (Render PostgreSQL)
✓ Future retrieval: Domain-filtered queries

---

## Conclusion

Your FlagTech system is now fully integrated with Render PostgreSQL for complete data persistence. All estimates, technicians, and assignments are:

✓ Saved to Render for permanent storage
✓ Filtered by domain for multi-tenant isolation
✓ Accessible for future reporting and analysis
✓ Ready for scaling to multiple companies

As you build and add features, all data continues to be retained and retrievable through domain-filtered queries from Render.
