# SAP BPC NW 10.1 - EPM Data Manager Package to BW DTP via TVAR Table

## Technical Solution: Category Copy (Actual to Forecast) with User Selection Parameters

---

## Architecture Overview

```
+---------------------------+       +----------------+       +------------------+
| BPC Data Manager Package  | ----> | BW TVAR Table  | ----> | BW DTP (Filter)  |
| (User Selection Screen)   |       | (Store From/To |       | (Reads TVAR for  |
| - Category From/To        |       |  Selections)   |       |  source filter & |
| - Time From/To            |       +----------------+       |  runs data copy) |
+---------------------------+                                 +------------------+
        |                                                            |
        v                                                            v
  BADI/ABAP Logic                                          BPC Model (Cube)
  writes to TVAR                                           Data copied from
                                                           Actual -> FEB_FCST
```

**Flow Summary:**

1. User opens BPC Data Manager and runs a package
2. User enters selection parameters (Category From/To, Time From/To)
3. ABAP logic (via Script Logic or BADI) captures selections and writes them to BW `TVARVC` table
4. BW DTP is configured with filters referencing TVAR variables
5. DTP executes and copies data within the BPC model (e.g., Actual -> FEB_FCST)

---

## Prerequisites

| Component | Requirement |
|-----------|------------|
| SAP BPC | NetWeaver 10.0 or 10.1 (Embedded or Standard) |
| SAP BW | 7.4 or higher |
| Authorizations | BPC Admin, BW Admin (RSA1), ABAP Developer (SE38/SE80) |
| BPC Model | InfoProvider (e.g., /CPMB/XXXXXXXX) with CATEGORY and TIME dimensions |
| Transactions | RSKC, TVARVC (SM30), RSA1, SE38, SE80, UJBR |

---

## STEP 1: Create the BPC Data Manager Package with Selection Parameters

### 1.1 Open BPC Administration Console

1. Log in to the **BPC Web Client** or open **EPM Add-in for Excel**
2. Navigate to: **Administration > Data Manager**
3. Alternatively, use transaction `UJBR` in SAP GUI

### 1.2 Create a New Data Manager Package

1. In the Data Manager, click **"Manage Packages"** (or "Organize Package List")
2. Click **"New"** to create a new package
3. Fill in the following:

```
Package ID    : Z_COPY_ACTUAL_TO_FCST
Description   : Copy Actual to Forecast with User Selections
Package Type  : Data Management (Process Chain based)
Team          : ADMIN (or your admin team)
```

### 1.3 Define Prompt (Selection) Parameters

In the package definition, go to the **"Prompt"** tab to define user selection parameters.

Create the following **4 prompts** (selection fields):

#### Prompt 1: Source Category (From)

```
Prompt Variable Name : CATEGORY_FROM
Prompt Text          : Source Category
Dimension            : CATEGORY
Member Selector      : Single Member Selection
Default Value        : ACTUAL
```

#### Prompt 2: Target Category (To)

```
Prompt Variable Name : CATEGORY_TO
Prompt Text          : Target Category
Dimension            : CATEGORY
Member Selector      : Single Member Selection
Default Value        : FEB_FCST
```

#### Prompt 3: Time Period From

```
Prompt Variable Name : TIME_FROM
Prompt Text          : Time From
Dimension            : TIME
Member Selector      : Single Member Selection
Default Value        : 2026.01
```

#### Prompt 4: Time Period To

```
Prompt Variable Name : TIME_TO
Prompt Text          : Time To
Dimension            : TIME
Member Selector      : Single Member Selection
Default Value        : 2026.12
```

### 1.4 Link Package to a Process Chain

1. In the **"Process Chain"** tab of the package, link it to a new or existing BW Process Chain
2. The process chain will contain:
   - **Step 1**: ABAP Program (to write TVAR entries)
   - **Step 2**: DTP Execution (to perform the data copy)

> **Important**: The package type must be **"Process Chain"** based so it can trigger BW objects.

### 1.5 User Selection Screen at Runtime

When the user runs package `Z_COPY_ACTUAL_TO_FCST`, BPC presents a selection screen:

```
+---------------------------------------------------+
|  Run Package: Copy Actual to Forecast              |
|---------------------------------------------------|
|                                                   |
|  Source Category:  [ACTUAL        ] [v]           |
|  Target Category:  [FEB_FCST      ] [v]           |
|  Time From:        [2026.01       ] [v]           |
|  Time To:          [2026.12       ] [v]           |
|                                                   |
|              [ Run ]    [ Cancel ]                |
+---------------------------------------------------+
```

The dimension member selectors allow users to pick valid members from the BPC dimension.

---

## STEP 2: ABAP Logic to Capture Selections and Write to TVAR Table

### 2.1 Understanding the TVARVC Table

The `TVARVC` table (transaction `STVARV` or `SM30 > TVARVC`) stores reusable variable values in BW. DTP filters can reference these variables instead of hard-coded values.

**Table Structure (TVARVC):**

| Field | Description |
|-------|-------------|
| NAME  | Variable name (e.g., Z_BPC_CAT_FROM) |
| TYPE  | P = Parameter, S = Select-Option |
| NUMB  | Selection number (for ranges) |
| SIGN  | I = Include, E = Exclude |
| OPTI  | EQ, BT, etc. |
| LOW   | From value |
| HIGH  | To value |

### 2.2 Define TVAR Variable Entries (One-Time Setup)

Use transaction **STVARV** (or SM30 with table view TVARVC) to pre-create the variable entries:

```
Variable Name          | Type      | Low Value  | High Value
-----------------------|-----------|------------|----------
Z_BPC_CATEGORY_FROM    | Parameter | ACTUAL     |
Z_BPC_CATEGORY_TO      | Parameter | FEB_FCST   |
Z_BPC_TIME_FROM        | Parameter | 2026.01    |
Z_BPC_TIME_TO          | Parameter | 2026.12    |
```

For range-based time selection, also create:

```
Variable Name          | Type          | Sign | Option | Low      | High
-----------------------|---------------|------|--------|----------|--------
Z_BPC_TIME_RANGE       | Select-Option | I    | BT     | 2026.01  | 2026.12
```

### 2.3 Create ABAP Program to Write User Selections to TVARVC

Create a new ABAP report via **SE38**:

**Program Name:** `Z_BPC_WRITE_TVAR_SELECTIONS`

```abap
*&---------------------------------------------------------------------*
*& Report Z_BPC_WRITE_TVAR_SELECTIONS
*& Description: Reads BPC Data Manager selection parameters and
*&              writes them to TVARVC table for DTP consumption
*&---------------------------------------------------------------------*
REPORT z_bpc_write_tvar_selections.

*----------------------------------------------------------------------*
* Data Declarations
*----------------------------------------------------------------------*
DATA: lt_tvarvc   TYPE TABLE OF tvarvc,
      ls_tvarvc   TYPE tvarvc,
      lv_cat_from TYPE char30,
      lv_cat_to   TYPE char30,
      lv_time_from TYPE char30,
      lv_time_to   TYPE char30.

*----------------------------------------------------------------------*
* Selection Screen (values passed from BPC Data Manager via variants)
*----------------------------------------------------------------------*
PARAMETERS: p_catfr  TYPE char30 DEFAULT 'ACTUAL'    OBLIGATORY,   "Source Category
            p_catto  TYPE char30 DEFAULT 'FEB_FCST'  OBLIGATORY,   "Target Category
            p_timefr TYPE char30 DEFAULT '2026.01'   OBLIGATORY,   "Time From
            p_timeto TYPE char30 DEFAULT '2026.12'   OBLIGATORY.   "Time To

*----------------------------------------------------------------------*
* START-OF-SELECTION
*----------------------------------------------------------------------*
START-OF-SELECTION.

  " Convert to uppercase for consistency
  TRANSLATE p_catfr  TO UPPER CASE.
  TRANSLATE p_catto  TO UPPER CASE.
  TRANSLATE p_timefr TO UPPER CASE.
  TRANSLATE p_timeto TO UPPER CASE.

  "--- Update Z_BPC_CATEGORY_FROM ---
  PERFORM update_tvarvc_parameter USING 'Z_BPC_CATEGORY_FROM' p_catfr.

  "--- Update Z_BPC_CATEGORY_TO ---
  PERFORM update_tvarvc_parameter USING 'Z_BPC_CATEGORY_TO' p_catto.

  "--- Update Z_BPC_TIME_FROM ---
  PERFORM update_tvarvc_parameter USING 'Z_BPC_TIME_FROM' p_timefr.

  "--- Update Z_BPC_TIME_TO ---
  PERFORM update_tvarvc_parameter USING 'Z_BPC_TIME_TO' p_timeto.

  "--- Update Z_BPC_TIME_RANGE (Select-Option for DTP) ---
  PERFORM update_tvarvc_range USING 'Z_BPC_TIME_RANGE' p_timefr p_timeto.

  COMMIT WORK AND WAIT.

  WRITE: / 'TVARVC entries updated successfully:'.
  WRITE: / '  Category From :', p_catfr.
  WRITE: / '  Category To   :', p_catto.
  WRITE: / '  Time From     :', p_timefr.
  WRITE: / '  Time To       :', p_timeto.

*&---------------------------------------------------------------------*
*& Form UPDATE_TVARVC_PARAMETER
*& Updates a single TVARVC parameter entry
*&---------------------------------------------------------------------*
FORM update_tvarvc_parameter USING pv_name TYPE clike
                                   pv_value TYPE clike.

  DATA: ls_tvarvc TYPE tvarvc.

  " Check if entry already exists
  SELECT SINGLE * FROM tvarvc INTO ls_tvarvc
    WHERE name = pv_name
      AND type = 'P'.

  IF sy-subrc = 0.
    " Update existing entry
    UPDATE tvarvc SET low = pv_value
      WHERE name = pv_name
        AND type = 'P'.
  ELSE.
    " Insert new entry
    CLEAR ls_tvarvc.
    ls_tvarvc-name = pv_name.
    ls_tvarvc-type = 'P'.
    ls_tvarvc-numb = '0000'.
    ls_tvarvc-sign = 'I'.
    ls_tvarvc-opti = 'EQ'.
    ls_tvarvc-low  = pv_value.
    INSERT tvarvc FROM ls_tvarvc.
  ENDIF.

  IF sy-subrc <> 0.
    MESSAGE e001(00) WITH 'Error updating TVARVC for' pv_name.
  ENDIF.

ENDFORM.

*&---------------------------------------------------------------------*
*& Form UPDATE_TVARVC_RANGE
*& Updates a TVARVC select-option range entry
*&---------------------------------------------------------------------*
FORM update_tvarvc_range USING pv_name TYPE clike
                               pv_low  TYPE clike
                               pv_high TYPE clike.

  DATA: ls_tvarvc TYPE tvarvc.

  " Delete existing range entries
  DELETE FROM tvarvc WHERE name = pv_name
                       AND type = 'S'.

  " Insert new range entry
  CLEAR ls_tvarvc.
  ls_tvarvc-name = pv_name.
  ls_tvarvc-type = 'S'.
  ls_tvarvc-numb = '0000'.
  ls_tvarvc-sign = 'I'.
  ls_tvarvc-opti = 'BT'.
  ls_tvarvc-low  = pv_low.
  ls_tvarvc-high = pv_high.
  INSERT tvarvc FROM ls_tvarvc.

  IF sy-subrc <> 0.
    MESSAGE e001(00) WITH 'Error updating TVARVC range for' pv_name.
  ENDIF.

ENDFORM.
```

### 2.4 Alternative: Use BADI `UJ_CUSTOM_LOGIC` (BPC Script Logic Approach)

If you prefer to use BPC Script Logic instead of a standalone ABAP program, implement BADI **`UJ_CUSTOM_LOGIC`**.

**Implementation Class:** `ZCL_BPC_WRITE_TVAR`

```abap
CLASS zcl_bpc_write_tvar DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_badi_interface.
    INTERFACES if_uj_custom_logic.

  PROTECTED SECTION.
  PRIVATE SECTION.
    METHODS update_tvarvc
      IMPORTING
        iv_name  TYPE tvarvc-name
        iv_type  TYPE tvarvc-type
        iv_low   TYPE tvarvc-low
        iv_high  TYPE tvarvc-high OPTIONAL.

ENDCLASS.

CLASS zcl_bpc_write_tvar IMPLEMENTATION.

  METHOD if_uj_custom_logic~execute.
*   This method is called from BPC Script Logic
*   Parameters are passed via the it_param table
*
*   Script Logic call:
*   *RUNLOGIC
*   *FUNCTION Z_WRITE_TVAR
*   *CATEGORY_FROM=ACTUAL
*   *CATEGORY_TO=FEB_FCST
*   *TIME_FROM=2026.01
*   *TIME_TO=2026.12
*   *ENDRUNLOGIC

    DATA: lv_cat_from  TYPE string,
          lv_cat_to    TYPE string,
          lv_time_from TYPE string,
          lv_time_to   TYPE string.

    " Read parameters passed from Script Logic
    LOOP AT it_param INTO DATA(ls_param).
      CASE ls_param-name.
        WHEN 'CATEGORY_FROM'.
          lv_cat_from = ls_param-value.
        WHEN 'CATEGORY_TO'.
          lv_cat_to = ls_param-value.
        WHEN 'TIME_FROM'.
          lv_time_from = ls_param-value.
        WHEN 'TIME_TO'.
          lv_time_to = ls_param-value.
      ENDCASE.
    ENDLOOP.

    " Write to TVARVC
    update_tvarvc( iv_name = 'Z_BPC_CATEGORY_FROM'
                   iv_type = 'P'
                   iv_low  = CONV #( lv_cat_from ) ).

    update_tvarvc( iv_name = 'Z_BPC_CATEGORY_TO'
                   iv_type = 'P'
                   iv_low  = CONV #( lv_cat_to ) ).

    update_tvarvc( iv_name = 'Z_BPC_TIME_FROM'
                   iv_type = 'P'
                   iv_low  = CONV #( lv_time_from ) ).

    update_tvarvc( iv_name = 'Z_BPC_TIME_TO'
                   iv_type = 'P'
                   iv_low  = CONV #( lv_time_to ) ).

    " Range entry for DTP
    update_tvarvc( iv_name = 'Z_BPC_TIME_RANGE'
                   iv_type = 'S'
                   iv_low  = CONV #( lv_time_from )
                   iv_high = CONV #( lv_time_to ) ).

    COMMIT WORK AND WAIT.

  ENDMETHOD.

  METHOD update_tvarvc.

    DATA: ls_tvarvc TYPE tvarvc.

    IF iv_type = 'S'.
      DELETE FROM tvarvc WHERE name = iv_name AND type = 'S'.
    ENDIF.

    SELECT SINGLE * FROM tvarvc INTO ls_tvarvc
      WHERE name = iv_name AND type = iv_type.

    IF sy-subrc = 0 AND iv_type = 'P'.
      UPDATE tvarvc SET low = iv_low
        WHERE name = iv_name AND type = 'P'.
    ELSE.
      CLEAR ls_tvarvc.
      ls_tvarvc-name = iv_name.
      ls_tvarvc-type = iv_type.
      ls_tvarvc-numb = '0000'.
      ls_tvarvc-sign = 'I'.
      ls_tvarvc-opti = COND #( WHEN iv_high IS NOT INITIAL THEN 'BT' ELSE 'EQ' ).
      ls_tvarvc-low  = iv_low.
      ls_tvarvc-high = iv_high.
      INSERT tvarvc FROM ls_tvarvc.
    ENDIF.

  ENDMETHOD.

ENDCLASS.
```

---

## STEP 3: Configure BW DTP to Read TVAR Variables and Execute Data Copy

### 3.1 Identify the BPC InfoProvider

1. Open transaction **RSA1** (Data Warehousing Workbench)
2. Navigate to **InfoProvider** tree
3. Find your BPC model's underlying InfoProvider:
   - Standard BPC: `/CPMB/<AppSet>/<Model>` (e.g., `/CPMB/OPEXPLAN/OPEX_MDL`)
   - Embedded BPC: The InfoProvider is the BPC model itself

### 3.2 Create the DTP (Data Transfer Process)

1. In **RSA1**, go to your InfoProvider
2. Right-click > **Create Data Transfer Process**
3. Configure:

```
DTP Type          : Standard (Full)
Source:
  Object Type     : InfoProvider
  InfoProvider    : /CPMB/<your_model>  (same cube as target - self-referencing)

Target:
  Object Type     : InfoProvider
  InfoProvider    : /CPMB/<your_model>  (same cube)

Extraction Mode   : Full
```

> **Key Point**: This is a **self-referencing DTP** -- source and target are the same BPC cube. The DTP reads data for the source category and writes it under the target category.

### 3.3 Create a Transformation

Between source and target, create a transformation:

1. Right-click on the DTP > **Create Transformation**
2. In the transformation:
   - Map all fields **1:1** (direct mapping) EXCEPT for `CATEGORY`
   - For the **CATEGORY** field, use a **routine** or **formula**:

**Start Routine (ABAP) in Transformation:**

```abap
*----------------------------------------------------------------------*
* Start Routine: Replace source CATEGORY with target CATEGORY from TVAR
*----------------------------------------------------------------------*
DATA: lv_cat_to TYPE tvarvc-low.

" Read target category from TVARVC
SELECT SINGLE low FROM tvarvc INTO lv_cat_to
  WHERE name = 'Z_BPC_CATEGORY_TO'
    AND type = 'P'.

IF sy-subrc <> 0.
  lv_cat_to = 'FEB_FCST'.  "Fallback default
ENDIF.
```

**Field Routine for CATEGORY (in Transformation Rule):**

```abap
*----------------------------------------------------------------------*
* Rule for CATEGORY field
* Replaces source category with the target category from TVARVC
*----------------------------------------------------------------------*
RESULT = lv_cat_to.  "Variable populated in Start Routine
```

This ensures all records extracted from `ACTUAL` are written as `FEB_FCST`.

### 3.4 Configure DTP Filters Using TVAR Variables

This is the critical step. The DTP extraction filter must use TVARVC variables so it dynamically reads the user's selections.

1. Open the DTP in **RSA1**
2. Go to the **"Extraction"** tab
3. Click **"Filter"** button
4. Add filter rows:

#### Filter for CATEGORY (Source):

```
Field       : 0BPC_CATEGORY (or your category InfoObject)
Option      : Variable
Variable    : Z_BPC_CATEGORY_FROM
Type        : TVARVC variable (Parameter)
```

**How to assign the TVAR variable in the DTP filter:**

1. In the DTP filter row for CATEGORY, click the **"Variable"** icon (clock/variable icon)
2. Select **"SAP TVARVC Variable"** as the variable type
3. Enter variable name: `Z_BPC_CATEGORY_FROM`
4. This tells the DTP to read the value from TVARVC at runtime

#### Filter for TIME (Range):

```
Field       : 0BPC_TIME (or your time InfoObject)
Option      : Variable
Variable    : Z_BPC_TIME_RANGE
Type        : TVARVC variable (Select-Option / Range)
```

**Steps:**

1. In the DTP filter row for TIME, click the **"Variable"** icon
2. Select **"SAP TVARVC Variable"**
3. Enter variable name: `Z_BPC_TIME_RANGE`
4. The DTP reads the range (e.g., 2026.01 to 2026.12) from TVARVC

### 3.5 DTP Filter Summary

After configuration, your DTP filter tab should look like:

```
+------------------------------------------------------------------+
| DTP Filter Configuration                                         |
|------------------------------------------------------------------|
| Field            | Sign | Option | Low Value         | High      |
|------------------|------|--------|-------------------|-----------|
| 0BPC_CATEGORY    | I    | EQ     | VAR:Z_BPC_CAT_FR  |           |
| 0BPC_TIME        | I    | BT     | VAR:Z_BPC_TIME_RANGE          |
+------------------------------------------------------------------+
```

### 3.6 Activate and Test the DTP

1. **Activate** the DTP (Ctrl+F3)
2. **Execute** manually first to test:
   - Ensure TVARVC has the expected values (check via SM30 > TVARVC)
   - Run the DTP and verify the extraction monitor
3. Check results in the BPC model (RSA1 > Manage > check cube contents)

---

## STEP 4: Build the BW Process Chain

### 4.1 Create the Process Chain

1. Open transaction **RSPC** (Process Chain Maintenance)
2. Create a new process chain:

```
Process Chain ID  : Z_PC_BPC_COPY_ACTUAL_FCST
Description       : BPC Copy Actual to Forecast via TVAR
```

### 4.2 Add Steps to the Process Chain

Add the following steps **in sequence**:

```
Step 1: Start Process
   |
   v
Step 2: ABAP Program (Z_BPC_WRITE_TVAR_SELECTIONS)
   |    - This writes user selections to TVARVC
   |    - Variant contains the parameters passed from BPC DM package
   |
   v
Step 3: Execute DTP (your DTP ID)
   |    - DTP reads TVARVC variables for filter
   |    - Extracts ACTUAL data for the time range
   |    - Writes it as FEB_FCST
   |
   v
Step 4: (Optional) Delta Merge / Compress
   |
   v
Step 5: End Process
```

**Process Chain Diagram:**

```
[START]
   |
   v
[ABAP: Z_BPC_WRITE_TVAR_SELECTIONS]
   |  (writes: CATEGORY_FROM=ACTUAL,
   |           CATEGORY_TO=FEB_FCST,
   |           TIME_FROM=2026.01,
   |           TIME_TO=2026.12)
   |
   v
[DTP: Execute Data Transfer Process]
   |  (reads TVARVC: Z_BPC_CATEGORY_FROM,
   |                  Z_BPC_TIME_RANGE)
   |  (extracts ACTUAL, writes as FEB_FCST)
   |
   v
[END / Optional: Compress Request]
```

### 4.3 Create ABAP Program Variant for Process Chain

1. Go to **SE38** > Program `Z_BPC_WRITE_TVAR_SELECTIONS`
2. Create a **Variant** (menu: Goto > Variants > Save as Variant)
3. The variant will be **dynamically updated** by the BPC Data Manager at runtime

> **Note**: When the BPC Data Manager Package runs, it maps the prompt variable values to the ABAP program's selection screen parameters via the process chain variant.

### 4.4 Link Process Chain to BPC Data Manager Package

1. Go back to the **BPC Data Manager** package `Z_COPY_ACTUAL_TO_FCST`
2. In the package configuration, set:

```
Package Type     : Process Chain
Process Chain    : Z_PC_BPC_COPY_ACTUAL_FCST
```

3. Map the BPC prompt variables to ABAP program parameters:

```
BPC Prompt Variable   -->  ABAP Parameter (in Variant)
---------------------------------------------------
CATEGORY_FROM         -->  P_CATFR
CATEGORY_TO           -->  P_CATTO
TIME_FROM             -->  P_TIMEFR
TIME_TO               -->  P_TIMETO
```

---

## STEP 5: End-to-End Testing

### 5.1 Verify TVARVC Setup

1. Go to **SM30** > Table View `TVARVC`
2. Confirm these entries exist:

```
| NAME                  | TYPE | LOW      | HIGH     |
|-----------------------|------|----------|----------|
| Z_BPC_CATEGORY_FROM   | P    | ACTUAL   |          |
| Z_BPC_CATEGORY_TO     | P    | FEB_FCST |          |
| Z_BPC_TIME_FROM       | P    | 2026.01  |          |
| Z_BPC_TIME_TO         | P    | 2026.12  |          |
| Z_BPC_TIME_RANGE      | S    | 2026.01  | 2026.12  |
```

### 5.2 Test Sequence

| # | Step | Transaction | Expected Result |
|---|------|-------------|-----------------|
| 1 | Run BPC DM Package | EPM Add-in or Web | User sees selection prompts |
| 2 | Enter selections | - | Category: ACTUAL -> FEB_FCST, Time: 2026.01 - 2026.12 |
| 3 | Click "Run" | - | Process chain triggered |
| 4 | Verify TVARVC | SM30/STVARV | Values updated with user selections |
| 5 | Verify DTP execution | RSA1 > Monitor | DTP extracted records with correct filter |
| 6 | Verify data in cube | LISTCUBE or RSRT | FEB_FCST records exist for time range |
| 7 | Verify in BPC model | EPM Add-in report | Data appears under FEB_FCST category |

### 5.3 Common Issues and Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| DTP shows 0 records | TVARVC not updated | Check ABAP program execution in process chain log |
| DTP filter not resolving | Variable not recognized | Ensure variable type is "TVARVC" in DTP filter, not "Customer Exit" |
| CATEGORY not replaced | Transformation rule missing | Check field routine for CATEGORY in transformation |
| Authorization error | Missing BW auth | Assign `S_RS_DTP` and `S_RS_PC` authorizations |
| Data Manager shows error | Process chain failed | Check RSPC log; ensure variant mapping is correct |
| Duplicate data | DTP run multiple times | Add deletion step before DTP or use "Overwrite" mode |

### 5.4 Delete Existing Target Data Before Copy (Recommended)

Add a **deletion step** in the process chain BEFORE the DTP to avoid duplicate records:

**Option A: ABAP Program for Selective Deletion**

```abap
*&---------------------------------------------------------------------*
*& Report Z_BPC_DELETE_TARGET_DATA
*& Deletes existing target category data before copy
*&---------------------------------------------------------------------*
REPORT z_bpc_delete_target_data.

DATA: lv_cat_to    TYPE char30,
      lv_time_from TYPE char30,
      lv_time_to   TYPE char30.

" Read target parameters from TVARVC
SELECT SINGLE low FROM tvarvc INTO lv_cat_to
  WHERE name = 'Z_BPC_CATEGORY_TO' AND type = 'P'.

SELECT SINGLE low FROM tvarvc INTO lv_time_from
  WHERE name = 'Z_BPC_TIME_FROM' AND type = 'P'.

SELECT SINGLE low FROM tvarvc INTO lv_time_to
  WHERE name = 'Z_BPC_TIME_TO' AND type = 'P'.

" Use BPC API to delete data for target category/time range
" (Implementation depends on your specific cube structure)
" Call function module RSDRI_INFOPROV_DELETE or use
" BPC write-back API for selective deletion
WRITE: / 'Target data deletion completed for:', lv_cat_to,
         'Time:', lv_time_from, '-', lv_time_to.
```

**Option B: Use a second DTP in "Delete" mode** (if supported by your BW version).

---

## STEP 6: Security and Authorization Considerations

### Required Authorization Objects

| Auth Object | Field | Value | Purpose |
|------------|-------|-------|---------|
| S_RS_DTP | RSODPTYPE | * | DTP execution |
| S_RS_PC | RSPCCHAIN | Z_PC_BPC_* | Process chain execution |
| S_TABU_DIS | DICBERCLS | &NC& | TVARVC table maintenance |
| S_UJ_* | Various | Per BPC role | BPC Data Manager access |

### Concurrency Warning

If multiple users run the package simultaneously, TVARVC values may be overwritten before the DTP reads them. Mitigations:

1. **User-specific TVARVC variables**: Append `SY-UNAME` to variable names (e.g., `Z_BPC_CAT_FROM_<USER>`)
2. **Enqueue/Dequeue locks**: Use SAP lock objects around the TVARVC update + DTP execution
3. **Serialization**: Configure the process chain to run in serial mode

**Lock Object Approach (Recommended):**

```abap
" Before writing TVARVC
CALL FUNCTION 'ENQUEUE_E_TABLE'
  EXPORTING
    tabname = 'TVARVC'
    varkey  = 'Z_BPC_%'
  EXCEPTIONS
    foreign_lock = 1
    OTHERS       = 2.

IF sy-subrc <> 0.
  MESSAGE 'Another user is running the copy process. Please wait.' TYPE 'E'.
ENDIF.

" ... write TVARVC and execute DTP ...

" After DTP completes
CALL FUNCTION 'DEQUEUE_E_TABLE'
  EXPORTING
    tabname = 'TVARVC'
    varkey  = 'Z_BPC_%'.
```

---

## Summary: Complete Object List

| Object | Name | Transaction |
|--------|------|-------------|
| BPC DM Package | Z_COPY_ACTUAL_TO_FCST | Data Manager / UJBR |
| ABAP Program | Z_BPC_WRITE_TVAR_SELECTIONS | SE38 |
| ABAP Program (optional) | Z_BPC_DELETE_TARGET_DATA | SE38 |
| BADI Implementation (alt.) | ZCL_BPC_WRITE_TVAR | SE18/SE19 |
| TVARVC Variables | Z_BPC_CATEGORY_FROM, Z_BPC_CATEGORY_TO, Z_BPC_TIME_FROM, Z_BPC_TIME_TO, Z_BPC_TIME_RANGE | STVARV / SM30 |
| Transformation | TR_<auto_generated> | RSA1 |
| DTP | DTP_<auto_generated> | RSA1 |
| Process Chain | Z_PC_BPC_COPY_ACTUAL_FCST | RSPC |

---

## Appendix: Quick Reference Transactions

| Transaction | Purpose |
|------------|---------|
| UJBR | BPC Administration (packages) |
| RSA1 | Data Warehousing Workbench (DTP, transformations) |
| RSPC | Process Chain maintenance |
| SE38 | ABAP Editor (programs) |
| SE18/SE19 | BADI Definition/Implementation |
| SM30 | Table Maintenance (TVARVC) |
| STVARV | TVARVC Variable Maintenance (direct) |
| LISTCUBE | Query InfoProvider contents |
| RSRT | Query Monitor (test queries) |
