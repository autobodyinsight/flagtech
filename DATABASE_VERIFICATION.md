# Database Integration Verification

## Database Connection
- **Database Provider**: PostgreSQL on Render.com
- **Connection File**: `app/services/db.py`
- **Connection Function**: `get_conn()` - Returns persistent connection with SSL
- **Database URL**: Stored in environment variable `DATABASE_URL`

---

## All Windows/Screens Database Status

### ✅ 1. DASHBOARD
**Location**: `app/routes/UI/dashboard.py`

**Reads From Database**:
- `saved_estimates` table - Gets all RO data (vehicle, customer, totals)
- `ro_assignments` table - Gets tech assignments for labor/paint
- `ro_notes` table - Gets notes for each RO

**API Endpoints Used**:
- `GET /api/dashboard-data` - Main dashboard metrics
- `GET /api/ro-notes` - Load notes for ROs
- `POST /api/ro-notes` - Save notes
- `POST /api/ro-phone` - Update phone numbers
- `POST /api/ro-assignments` - Assign techs to ROs
- `POST /api/flash` - Delete all estimate data

**Status**: ✅ All API calls use relative paths, properly authenticated with domain isolation

---

### ✅ 2. UPLOAD
**Location**: `app/routes/UI/upload_ui/`

**Saves To Database**:
- `saved_estimates` table - Saves complete estimate data:
  - RO number, vehicle info, VIN
  - Owner info, insurance, claim number
  - Labor repairs (JSONB)
  - Paint repairs (JSONB)
  - Parts repairs (JSONB)
  - Estimate totals (JSONB)
  - Financial totals (grand_total, deductible, customer_pay, insurance_pay)
  - Domain (for multi-tenant isolation)

**API Endpoints Used**:
- `POST /ui/save-estimate` - Saves parsed estimate data

**Backend Handler**: `app/routes/UI/ui_with_processing.py` - save_estimate()

**Status**: ✅ Properly saves to Render database with domain isolation

---

### ✅ 3. TECHS
**Location**: `app/routes/UI/techs.py`

**Database Tables**:
- `techs` table - Stores technician information
- `ro_assignments` table - Stores RO assignments to techs

**Saves To Database**:
- Technician records (first_name, last_name, pay_rate, domain, active)

**Reads From Database**:
- List of active technicians
- Tech assignments per RO
- RO repair lines for assignment

**API Endpoints Used**:
- `POST /api/techs/add` - Add new technician
- `GET /api/techs/list` - List all active technicians
- `POST /api/techs/delete` - Soft delete technician (set active=false)
- `GET /api/tech-assignments` - Get assignments for a tech
- `GET /api/ro-repairs` - Get repair lines for assignment modal

**Status**: ✅ All CRUD operations connected to database. **FIXED**: Added `_ensure_techs_table()` function to create table if missing

---

### ✅ 4. PHASE
**Location**: `app/routes/UI/phase.py`

**Database Tables**:
- `ro_phases` table - Stores current phase for each RO
- `saved_estimates` table - Reads RO data

**Saves To Database**:
- Phase updates (ro, phase, domain, updated_at)

**Reads From Database**:
- Phase board with all ROs and their phases
- Labor/paint hours per RO

**API Endpoints Used**:
- `POST /api/phase/update` - Update phase for an RO
- `GET /api/phase/board` - Get all ROs grouped by phase

**Status**: ✅ Full database integration with upsert logic (ON CONFLICT DO UPDATE)

---

### ✅ 5. PARTS
**Location**: `app/routes/UI/parts.py`

**Database Tables**:
- `parts_vendors` table - Stores vendor information
- `parts_orders` table - Stores parts orders
- `parts_received` table - Tracks received/returned parts
- `saved_estimates` table - Reads parts list from estimates

**Saves To Database**:
- Vendor records (name, email, phone, domain)
- Parts orders (ro, vendor_id, arrival_date, ordered_lines)
- Parts received/returned status

**Reads From Database**:
- Active vendors list
- RO parts lists
- Parts order status
- Arrival dates and counts

**API Endpoints Used**:
- `POST /api/vendors/add` - Add new vendor
- `GET /api/vendors/list` - List active vendors
- `GET /api/parts/ros` - List all ROs with parts
- `GET /api/parts/ro-lines` - Get parts lines for specific RO
- `POST /api/parts/order` - Create parts order
- `GET /api/parts/received` - Get received parts for RO
- `POST /api/parts/receive` - Mark parts as received/returned

**Status**: ✅ Complete parts management with vendor tracking

---

### ⚠️ 6. FLAGOUT
**Location**: `app/routes/UI/flagout.py`

**Status**: ⚠️ Placeholder only - "coming soon" message, no database integration yet

---

## Database Tables Summary

### Core Tables (All on Render PostgreSQL)

1. **saved_estimates** - Main estimate storage
   - Stores: RO data, vehicle info, labor/paint/parts repairs, totals
   - Used by: Dashboard, Upload, Phase, Parts, Techs

2. **techs** - Technician records
   - Stores: first_name, last_name, pay_rate, domain, active
   - Used by: Techs screen, Dashboard (for assignments)

3. **ro_assignments** - Tech assignments to ROs
   - Stores: ro, role (labor/paint), tech_id, tech_name, excluded_lines, assigned_hours, domain
   - Used by: Dashboard, Techs

4. **ro_phases** - Phase tracking for ROs
   - Stores: ro, phase, domain, updated_at
   - Used by: Phase screen

5. **parts_vendors** - Parts vendor information
   - Stores: name, email, phone, domain, active
   - Used by: Parts screen

6. **parts_orders** - Parts order tracking
   - Stores: ro, vendor_id, arrival_date, ordered_lines, arrived_count, returned_count, domain
   - Used by: Parts screen

7. **parts_received** - Individual parts receipt tracking
   - Stores: ro, line, description, received, returned, domain
   - Used by: Parts screen

8. **ro_notes** - Notes attached to ROs
   - Stores: ro, note, domain, created_at
   - Used by: Dashboard

9. **users** - User authentication
   - Stores: email, domain, company_name, password_hash, active
   - Used by: Authentication system

10. **sessions** - Persistent login sessions
    - Stores: token, user_id, email, domain, expires_at
    - Used by: Authentication middleware

---

## Multi-Tenant Isolation

All tables use `domain` column for tenant isolation:
- Extracted from request headers, cookies, or origin via `get_user_domain(request)`
- All queries filter by domain: `WHERE domain = %s`
- Prevents data leakage between different customers

---

## API Endpoint Summary

### Working Endpoints (All Connected to Render Database)

**Estimates & Dashboard**:
- ✅ `GET /api/dashboard-data` - Dashboard metrics
- ✅ `POST /api/flash` - Clear all data
- ✅ `GET /api/ro-notes` - Get RO notes  
- ✅ `POST /api/ro-notes` - Save RO note
- ✅ `POST /api/ro-phone` - Update phone
- ✅ `GET /api/ro-repairs` - Get repair lines
- ✅ `POST /api/ro-assignments` - Assign tech to RO

**Technicians**:
- ✅ `POST /api/techs/add` - Add technician
- ✅ `GET /api/techs/list` - List technicians
- ✅ `POST /api/techs/delete` - Delete technician
- ✅ `GET /api/tech-assignments` - Get tech's assignments

**Phase Management**:
- ✅ `POST /api/phase/update` - Update RO phase
- ✅ `GET /api/phase/board` - Get phase board data

**Parts Management**:
- ✅ `POST /api/vendors/add` - Add vendor
- ✅ `GET /api/vendors/list` - List vendors
- ✅ `GET /api/parts/ros` - List ROs with parts
- ✅ `GET /api/parts/ro-lines` - Get RO parts lines
- ✅ `POST /api/parts/order` - Create parts order
- ✅ `GET /api/parts/received` - Get received parts
- ✅ `POST /api/parts/receive` - Mark parts received/returned

**Upload**:
- ✅ `POST /ui/save-estimate` - Save uploaded estimate

---

## Recent Fixes Applied

### 1. ✅ Fixed Hardcoded Backend URLs
**Issue**: Dashboard and Techs screens used hardcoded `https://flagtech1.onrender.com`  
**Fix**: Changed all API calls to use relative paths (`/api/...`)  
**Benefit**: Works regardless of domain, proper authentication

### 2. ✅ Added Missing Techs Table
**Issue**: Techs table was used but never created  
**Fix**: Added `_ensure_techs_table()` function with proper schema  
**Impact**: Techs screen now works properly with automatic table creation

### 3. ✅ Added credentials: 'include' to API calls
**Issue**: Some calls missing authentication headers  
**Fix**: Added `credentials: 'include'` to all fetch calls  
**Benefit**: Proper session/cookie handling for domain detection

---

## Verification Checklist

- ✅ All database tables have proper indexes (domain, ro, etc.)
- ✅ All tables use multi-tenant isolation with `domain` column
- ✅ All API endpoints validate domain authentication
- ✅ All frontend API calls use relative paths
- ✅ All endpoints include `credentials: 'include'` for authentication
- ✅ Table creation is automatic via `_ensure_*_table()` functions
- ✅ JSONB columns used for flexible data (repairs, totals, notes)
- ✅ Proper foreign key relationships (tech_id references techs.id)
- ✅ Soft delete pattern used (active=false instead of DELETE)
- ✅ Timestamps tracked (created_at, updated_at, saved_at)

---

## Database Schema Files

- `create_users_table.sql` - Initial schema for users/sessions/vendors
- `init_db.py` - Python script to initialize/migrate database
- `app/routes/estimate.py` - Contains all `_ensure_*_table()` functions

---

## Conclusion

✅ **ALL WINDOWS ARE FULLY INTEGRATED WITH RENDER DATABASE**

Every screen (except Flagout placeholder) properly:
1. Saves data to PostgreSQL on Render
2. Retrieves data from PostgreSQL on Render  
3. Uses domain-based isolation for multi-tenancy
4. Uses relative API paths for proper routing
5. Includes authentication for security

The application is production-ready with full database persistence.
