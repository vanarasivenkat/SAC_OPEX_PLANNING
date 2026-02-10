# Complete BADI Implementation Guide
# BPC NW 10.1: Data Manager Selections to TVARVC for DTP Consumption

---

## Table of Contents

1. [BADI Overview and Selection](#1-badi-overview-and-selection)
2. [Step-by-Step: Create Enhancement Implementation (SE19)](#2-step-by-step-create-enhancement-implementation)
3. [Complete BADI Class Code - UJ_CUSTOM_LOGIC](#3-complete-badi-class-code---uj_custom_logic)
4. [Complete BADI Class Code - UJO_BADI_DM_PACKAGE (Alternative)](#4-complete-badi-class-code---ujo_badi_dm_package)
5. [Script Logic File to Trigger BADI](#5-script-logic-file-to-trigger-badi)
6. [Data Manager Package Configuration](#6-data-manager-package-configuration)
7. [Testing and Debugging](#7-testing-and-debugging)
8. [Appendix: Full Class Dictionary Objects](#8-appendix)

---

## 1. BADI Overview and Selection

### Which BADI to Use?

There are **two BADI approaches** for this scenario. Choose based on your package type:

| BADI | Enhancement Spot | Package Type | When to Use |
|------|-----------------|--------------|-------------|
| **`UJ_CUSTOM_LOGIC`** | `UJ_ES_CUSTOM_LOGIC` | Script Logic | **Recommended.** Most common. BPC Script Logic calls custom ABAP function via `*FUNCTION` keyword. |
| **`UJO_BADI_DM_PACKAGE`** | `UJO_ES_DM_PACKAGE` | Process Chain | Alternative. Intercepts Data Manager package execution directly. Gives access to all prompt selections. |

### Recommendation

Use **`UJ_CUSTOM_LOGIC`** (Approach A). It is:
- The standard SAP-recommended approach for custom ABAP in BPC NW
- Well-documented by SAP
- Gives full access to user selections via parameter passing
- Works with Script Logic packages (most flexible)

---

## 2. Step-by-Step: Create Enhancement Implementation

### APPROACH A: BADI `UJ_CUSTOM_LOGIC`

---

### Step 2.1: Open Transaction SE19

1. Log into SAP GUI
2. Enter transaction **`SE19`** (BADI Implementation)
3. You will see the initial screen:

```
+------------------------------------------------------------------+
|  Enhancement Implementation                                       |
|------------------------------------------------------------------|
|                                                                  |
|  (*) Create Implementation                                       |
|                                                                  |
|  Enhancement Spot:  [                              ]             |
|                                                                  |
|           [ Display ]  [ Create ]                                |
+------------------------------------------------------------------+
```

### Step 2.2: Find the Enhancement Spot

1. Select radio button **"Create Implementation"**
2. In the **Enhancement Spot** field, enter: **`UJ_ES_CUSTOM_LOGIC`**
3. Click **"Create"** (or press F5)

> If you don't know the enhancement spot name, click the search help (F4) and search for `UJ*CUSTOM*`.

### Step 2.3: Confirm BADI Definition

The system shows the BADI definition details:

```
+------------------------------------------------------------------+
|  BADI Definition: UJ_CUSTOM_LOGIC                                |
|------------------------------------------------------------------|
|  Enhancement Spot : UJ_ES_CUSTOM_LOGIC                           |
|  BADI Interface   : IF_UJ_CUSTOM_LOGIC                           |
|  Multiple Use     : Yes (filter-based)                           |
|  Filter Type      : UJKT_CUSTOM_LOGIC (Function Name)           |
|------------------------------------------------------------------|
|  Interface Methods:                                              |
|    EXECUTE  - Execute custom logic                               |
+------------------------------------------------------------------+
```

### Step 2.4: Create Enhancement Implementation

1. A popup appears asking for the implementation name:

```
+------------------------------------------+
|  Create Enhancement Implementation       |
|------------------------------------------|
|  Implementation Name: [Z_EI_BPC_TVAR   ] |
|  Description:         [BPC Selections    ]|
|                       [to TVARVC         ]|
|         [ Continue ]  [ Cancel ]         |
+------------------------------------------+
```

2. Enter:
   - **Implementation Name**: `Z_EI_BPC_WRITE_TVAR`
   - **Description**: `BPC Data Manager Selections to TVARVC Table`
3. Click **Continue**

### Step 2.5: Create BADI Implementation

1. On the Enhancement Implementation screen, you see the tree on the left
2. Right-click on **"BADI Implementations"** node > **"Create BADI Implementation"**

```
+------------------------------------------+
|  Create BADI Implementation              |
|------------------------------------------|
|  BADI Definition:    [UJ_CUSTOM_LOGIC  ] |
|  Implementation Name:[Z_BI_BPC_TVAR    ] |
|  Description:        [Write BPC          |
|                       selections to TVAR]|
|         [ Continue ]  [ Cancel ]         |
+------------------------------------------+
```

3. Enter:
   - **BADI Definition**: `UJ_CUSTOM_LOGIC`
   - **Implementation Name**: `Z_BI_BPC_WRITE_TVAR`
   - **Description**: `Write BPC DM selections to TVARVC for DTP`
4. Click **Continue**

### Step 2.6: Set the Filter Value

This is **critical**. The BADI `UJ_CUSTOM_LOGIC` uses a **filter** to determine which implementation to call. The filter value must match the `*FUNCTION` name used in Script Logic.

1. In the BADI Implementation details, find the **"Filter Value"** tab/section
2. Click on the filter row
3. Enter the filter value:

```
+------------------------------------------------------------------+
|  Filter Values                                                    |
|------------------------------------------------------------------|
|  Filter Type: UJKT_CUSTOM_LOGIC                                  |
|                                                                  |
|  Combination | Filter Value                                     |
|  001         | Z_WRITE_TVAR                                     |
+------------------------------------------------------------------+
```

- **Filter Value**: `Z_WRITE_TVAR`

> This must exactly match the `*FUNCTION` name in your Script Logic file (Step 5).

### Step 2.7: Create the Implementing Class

1. In the BADI Implementation, find the **"Implementing Class"** field
2. Enter class name: **`ZCL_BPC_WRITE_TVAR`**

```
+------------------------------------------------------------------+
|  BADI Implementation: Z_BI_BPC_WRITE_TVAR                        |
|------------------------------------------------------------------|
|  BADI Definition    : UJ_CUSTOM_LOGIC                            |
|  Implementing Class : [ZCL_BPC_WRITE_TVAR                      ] |
|  Filter Value       : Z_WRITE_TVAR                               |
|  Active             : [X]                                        |
+------------------------------------------------------------------+
```

3. **Double-click** on the class name `ZCL_BPC_WRITE_TVAR`
4. The system asks: **"Class does not exist. Create?"** - Click **"Yes"**

### Step 2.8: Class Builder Opens (SE24 embedded)

The Class Builder opens with a skeleton class:

```
+------------------------------------------------------------------+
|  Class Builder: ZCL_BPC_WRITE_TVAR                               |
|------------------------------------------------------------------|
|  Description: BADI Implementation - BPC to TVARVC                |
|  Instantiation: Public                                           |
|  Final: [X]                                                      |
|------------------------------------------------------------------|
|  Interfaces:                                                     |
|    IF_BADI_INTERFACE                                             |
|    IF_UJ_CUSTOM_LOGIC       <-- auto-added from BADI definition  |
|------------------------------------------------------------------|
|  Methods:                                                        |
|    IF_UJ_CUSTOM_LOGIC~EXECUTE  (inherited from interface)        |
+------------------------------------------------------------------+
```

The interface `IF_UJ_CUSTOM_LOGIC` is automatically added. You need to implement the `EXECUTE` method.

### Step 2.9: Check the Interface Method Signature

Before writing code, understand the EXECUTE method signature. Double-click on `IF_UJ_CUSTOM_LOGIC~EXECUTE` to see its parameters:

```
+------------------------------------------------------------------+
|  Method: IF_UJ_CUSTOM_LOGIC~EXECUTE                             |
|------------------------------------------------------------------|
|  Parameters:                                                     |
|                                                                  |
|  IMPORTING:                                                      |
|    IT_PARAM     TYPE UJK_T_SCRIPT_LOGIC_HASHTABLE               |
|                 (Table of name-value pairs from Script Logic)    |
|                                                                  |
|    IT_DATA      TYPE REF TO DATA                                 |
|                 (Reference to input data records)                |
|                                                                  |
|    IO_CALLER    TYPE REF TO IF_UJ_CONTEXT                       |
|                 (BPC context: AppSet, Application, User, etc.)   |
|                                                                  |
|  CHANGING:                                                       |
|    CT_DATA      TYPE REF TO DATA                                 |
|                 (Reference to output data records)               |
|                                                                  |
|  EXPORTING:                                                      |
|    ET_MESSAGE   TYPE UJ0_T_MESSAGE                              |
|                 (Messages returned to BPC - shown to user)       |
|                                                                  |
|    EV_FLAG      TYPE UJ_FLG                                     |
|                 (Return flag: ABAP_TRUE = success)               |
+------------------------------------------------------------------+
```

**Key Parameter Details:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `IT_PARAM` | `UJK_T_SCRIPT_LOGIC_HASHTABLE` | Hash table of name-value pairs. Each entry has fields `NAME` and `VALUE`. Contains parameters passed from Script Logic via `*FUNCTION` call. |
| `IT_DATA` | `REF TO DATA` | Reference to internal table with input records from BPC (the data scope). May be initial if no data scope. |
| `IO_CALLER` | `REF TO IF_UJ_CONTEXT` | Context object. Use to get AppSet name, Application name, User name, Environment ID, etc. |
| `CT_DATA` | `REF TO DATA` | Output data. Modify this to write data back to BPC. For our use case we don't write data, so leave as-is. |
| `ET_MESSAGE` | `UJ0_T_MESSAGE` | Return messages to the user. Shown in Data Manager log. |
| `EV_FLAG` | `UJ_FLG` | Set to `ABAP_TRUE` for success, `ABAP_FALSE` for failure. |

### Step 2.10: Enter the Class Code

Now enter the complete class code (see Section 3 below for the full code). After entering:

1. Click **"Check"** (Ctrl+F2) - Fix any syntax errors
2. Click **"Activate"** (Ctrl+F3)

### Step 2.11: Activate the Enhancement Implementation

1. Go back to the Enhancement Implementation screen (SE19)
2. Make sure the BADI Implementation is marked as **Active** (checkbox)
3. Click **"Activate"** (Ctrl+F3) on the Enhancement Implementation

```
+------------------------------------------------------------------+
|  Enhancement Implementation: Z_EI_BPC_WRITE_TVAR                |
|------------------------------------------------------------------|
|  Status: [Active]                                                |
|                                                                  |
|  BADI Implementations:                                           |
|    Z_BI_BPC_WRITE_TVAR                                          |
|      Class: ZCL_BPC_WRITE_TVAR                                  |
|      Filter: Z_WRITE_TVAR                                       |
|      Active: [X]                                                |
+------------------------------------------------------------------+
```

### Step 2.12: Verification Checklist

After activation, verify:

| # | Check | How |
|---|-------|-----|
| 1 | Enhancement Implementation active | SE19 > Z_EI_BPC_WRITE_TVAR > Status = Active |
| 2 | BADI Implementation active | Checkbox is ticked |
| 3 | Class exists and is active | SE24 > ZCL_BPC_WRITE_TVAR > Status = Active |
| 4 | Filter value correct | Z_WRITE_TVAR (must match Script Logic *FUNCTION) |
| 5 | Interface implemented | IF_UJ_CUSTOM_LOGIC with EXECUTE method |

---

## 3. Complete BADI Class Code - UJ_CUSTOM_LOGIC

### 3.1 Class Definition (Global Section)

Create this class in **SE24** or via the embedded class builder in SE19.

```abap
*----------------------------------------------------------------------*
* Class ZCL_BPC_WRITE_TVAR
* BADI Implementation for UJ_CUSTOM_LOGIC
* Purpose: Reads BPC Data Manager user selection parameters and
*          writes them to TVARVC table so BW DTP can consume them.
*
* Filter Value: Z_WRITE_TVAR
* Called from Script Logic: *FUNCTION Z_WRITE_TVAR
*
* Parameters expected from Script Logic:
*   CATEGORY_FROM - Source category (e.g., ACTUAL)
*   CATEGORY_TO   - Target category (e.g., FEB_FCST)
*   TIME_FROM     - Start period (e.g., 2026.01)
*   TIME_TO       - End period (e.g., 2026.12)
*----------------------------------------------------------------------*
CLASS zcl_bpc_write_tvar DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.

    "-- BADI Interface
    INTERFACES if_badi_interface.
    INTERFACES if_uj_custom_logic.

    "-- Constants for TVARVC variable names
    CONSTANTS:
      gc_tvar_cat_from  TYPE tvarvc-name VALUE 'Z_BPC_CATEGORY_FROM',
      gc_tvar_cat_to    TYPE tvarvc-name VALUE 'Z_BPC_CATEGORY_TO',
      gc_tvar_time_from TYPE tvarvc-name VALUE 'Z_BPC_TIME_FROM',
      gc_tvar_time_to   TYPE tvarvc-name VALUE 'Z_BPC_TIME_TO',
      gc_tvar_time_range TYPE tvarvc-name VALUE 'Z_BPC_TIME_RANGE'.

    "-- Constants for parameter names (must match Script Logic)
    CONSTANTS:
      gc_param_cat_from  TYPE string VALUE 'CATEGORY_FROM',
      gc_param_cat_to    TYPE string VALUE 'CATEGORY_TO',
      gc_param_time_from TYPE string VALUE 'TIME_FROM',
      gc_param_time_to   TYPE string VALUE 'TIME_TO'.

  PROTECTED SECTION.

  PRIVATE SECTION.

    "-- Structure to hold parsed parameters
    TYPES:
      BEGIN OF ty_selections,
        category_from TYPE string,
        category_to   TYPE string,
        time_from     TYPE string,
        time_to       TYPE string,
      END OF ty_selections.

    "-- Instance attributes
    DATA: ms_selections TYPE ty_selections,
          mv_appset     TYPE uj_appset_id,
          mv_appl       TYPE uj_appl_id,
          mv_user       TYPE sy-uname.

    "-- Private methods
    METHODS:
      parse_parameters
        IMPORTING
          it_param      TYPE ujk_t_script_logic_hashtable
        RETURNING
          VALUE(rv_ok)  TYPE abap_bool,

      validate_selections
        RETURNING
          VALUE(rv_ok)  TYPE abap_bool,

      acquire_lock
        RETURNING
          VALUE(rv_ok)  TYPE abap_bool,

      release_lock,

      update_tvarvc_parameter
        IMPORTING
          iv_name       TYPE tvarvc-name
          iv_value      TYPE clike
        RETURNING
          VALUE(rv_ok)  TYPE abap_bool,

      update_tvarvc_range
        IMPORTING
          iv_name       TYPE tvarvc-name
          iv_low        TYPE clike
          iv_high       TYPE clike
        RETURNING
          VALUE(rv_ok)  TYPE abap_bool,

      write_all_tvarvc_entries
        RETURNING
          VALUE(rv_ok)  TYPE abap_bool,

      add_message
        IMPORTING
          iv_type       TYPE symsgty
          iv_message    TYPE string
        CHANGING
          ct_message    TYPE uj0_t_message,

      log_to_application_log
        IMPORTING
          iv_message    TYPE string
          iv_type       TYPE symsgty DEFAULT 'I'.

ENDCLASS.


CLASS zcl_bpc_write_tvar IMPLEMENTATION.

*----------------------------------------------------------------------*
* METHOD if_uj_custom_logic~execute
* Main entry point - called by BPC Script Logic engine
*----------------------------------------------------------------------*
  METHOD if_uj_custom_logic~execute.

    DATA: lv_msg TYPE string.

    " Initialize return values
    ev_flag = abap_true.
    CLEAR et_message.

    "-- Step 1: Get context information
    IF io_caller IS BOUND.
      mv_appset = io_caller->appset_id.
      mv_appl   = io_caller->appl_id.
      mv_user   = sy-uname.
    ENDIF.

    log_to_application_log(
      iv_message = |BADI Z_WRITE_TVAR started by user { mv_user } for AppSet { mv_appset } / App { mv_appl }|
      iv_type    = 'I' ).

    add_message(
      EXPORTING iv_type    = 'I'
                iv_message = |Starting TVARVC update process...|
      CHANGING  ct_message = et_message ).

    "-- Step 2: Parse parameters from Script Logic
    IF parse_parameters( it_param ) = abap_false.
      ev_flag = abap_false.
      add_message(
        EXPORTING iv_type    = 'E'
                  iv_message = |ERROR: Failed to parse selection parameters. Check Script Logic file.|
        CHANGING  ct_message = et_message ).
      log_to_application_log(
        iv_message = 'ERROR: Parameter parsing failed'
        iv_type    = 'E' ).
      RETURN.
    ENDIF.

    add_message(
      EXPORTING iv_type    = 'I'
                iv_message = |Parsed: CAT_FROM={ ms_selections-category_from } | &&
                             |CAT_TO={ ms_selections-category_to } | &&
                             |TIME={ ms_selections-time_from } to { ms_selections-time_to }|
      CHANGING  ct_message = et_message ).

    "-- Step 3: Validate selections
    IF validate_selections( ) = abap_false.
      ev_flag = abap_false.
      add_message(
        EXPORTING iv_type    = 'E'
                  iv_message = |ERROR: Validation failed. Ensure all 4 parameters are provided.|
        CHANGING  ct_message = et_message ).
      RETURN.
    ENDIF.

    "-- Step 4: Acquire lock (prevent concurrent updates)
    IF acquire_lock( ) = abap_false.
      ev_flag = abap_false.
      add_message(
        EXPORTING iv_type    = 'E'
                  iv_message = |ERROR: Could not acquire lock on TVARVC. Another user may be running the same process.|
        CHANGING  ct_message = et_message ).
      RETURN.
    ENDIF.

    "-- Step 5: Write all TVARVC entries
    IF write_all_tvarvc_entries( ) = abap_true.
      COMMIT WORK AND WAIT.
      add_message(
        EXPORTING iv_type    = 'I'
                  iv_message = |SUCCESS: TVARVC entries updated. DTP can now execute with these filters.|
        CHANGING  ct_message = et_message ).
      log_to_application_log(
        iv_message = |TVARVC updated: { ms_selections-category_from }->{ ms_selections-category_to }, | &&
                     |Time { ms_selections-time_from }-{ ms_selections-time_to }|
        iv_type    = 'S' ).
    ELSE.
      ROLLBACK WORK.
      ev_flag = abap_false.
      add_message(
        EXPORTING iv_type    = 'E'
                  iv_message = |ERROR: Failed to update one or more TVARVC entries. Changes rolled back.|
        CHANGING  ct_message = et_message ).
      log_to_application_log(
        iv_message = 'ERROR: TVARVC update failed, rolled back'
        iv_type    = 'E' ).
    ENDIF.

    "-- Step 6: Release lock
    release_lock( ).

    add_message(
      EXPORTING iv_type    = 'I'
                iv_message = |BADI Z_WRITE_TVAR completed. Return flag = { ev_flag }.|
      CHANGING  ct_message = et_message ).

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD parse_parameters
* Reads name-value pairs from the Script Logic IT_PARAM table
*----------------------------------------------------------------------*
  METHOD parse_parameters.

    DATA: ls_param TYPE ujk_s_script_logic_hashtable.

    rv_ok = abap_true.
    CLEAR ms_selections.

    IF it_param IS INITIAL.
      rv_ok = abap_false.
      RETURN.
    ENDIF.

    LOOP AT it_param INTO ls_param.

      " Parameter names from Script Logic are passed in UPPERCASE
      DATA(lv_name) = to_upper( ls_param-hashtable_key ).
      DATA(lv_value) = ls_param-hashtable_value.

      " Trim leading/trailing spaces
      CONDENSE lv_value.
      TRANSLATE lv_value TO UPPER CASE.

      CASE lv_name.
        WHEN gc_param_cat_from.
          ms_selections-category_from = lv_value.
        WHEN gc_param_cat_to.
          ms_selections-category_to = lv_value.
        WHEN gc_param_time_from.
          ms_selections-time_from = lv_value.
        WHEN gc_param_time_to.
          ms_selections-time_to = lv_value.
        WHEN OTHERS.
          " Ignore unknown parameters (e.g., system parameters)
          CONTINUE.
      ENDCASE.

    ENDLOOP.

    " Check all required parameters were provided
    IF ms_selections-category_from IS INITIAL OR
       ms_selections-category_to   IS INITIAL OR
       ms_selections-time_from     IS INITIAL OR
       ms_selections-time_to       IS INITIAL.
      rv_ok = abap_false.
    ENDIF.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD validate_selections
* Validates that user selections are logically correct
*----------------------------------------------------------------------*
  METHOD validate_selections.

    rv_ok = abap_true.

    " Validate: Source and target categories must be different
    IF ms_selections-category_from = ms_selections-category_to.
      log_to_application_log(
        iv_message = |Validation Error: Source and target category are the same ({ ms_selections-category_from })|
        iv_type    = 'E' ).
      rv_ok = abap_false.
      RETURN.
    ENDIF.

    " Validate: TIME_FROM must not be greater than TIME_TO
    IF ms_selections-time_from > ms_selections-time_to.
      log_to_application_log(
        iv_message = |Validation Error: TIME_FROM ({ ms_selections-time_from }) > TIME_TO ({ ms_selections-time_to })|
        iv_type    = 'E' ).
      rv_ok = abap_false.
      RETURN.
    ENDIF.

    " Validate: Category values should not be empty after trimming
    IF ms_selections-category_from IS INITIAL OR
       ms_selections-category_to   IS INITIAL.
      rv_ok = abap_false.
      RETURN.
    ENDIF.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD acquire_lock
* Locks TVARVC entries to prevent concurrent modification
*----------------------------------------------------------------------*
  METHOD acquire_lock.

    rv_ok = abap_true.

    CALL FUNCTION 'ENQUEUE_E_TABLE'
      EXPORTING
        mode_rstable = 'E'
        tabname      = 'TVARVC'
        varkey       = 'Z_BPC_%'
        _scope       = '2'
        _wait        = 'X'           " Wait up to timeout if locked
      EXCEPTIONS
        foreign_lock   = 1
        system_failure = 2
        OTHERS         = 3.

    IF sy-subrc <> 0.
      rv_ok = abap_false.
      log_to_application_log(
        iv_message = |Lock failed on TVARVC (sy-subrc={ sy-subrc }, locked by { sy-msgv1 })|
        iv_type    = 'E' ).
    ENDIF.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD release_lock
* Releases the TVARVC table lock
*----------------------------------------------------------------------*
  METHOD release_lock.

    CALL FUNCTION 'DEQUEUE_E_TABLE'
      EXPORTING
        mode_rstable = 'E'
        tabname      = 'TVARVC'
        varkey       = 'Z_BPC_%'
        _scope       = '2'.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD update_tvarvc_parameter
* Updates or inserts a single TVARVC Parameter (Type P) entry
*----------------------------------------------------------------------*
  METHOD update_tvarvc_parameter.

    DATA: ls_tvarvc TYPE tvarvc.

    rv_ok = abap_true.

    " Check if entry exists
    SELECT SINGLE * FROM tvarvc INTO ls_tvarvc
      WHERE name = iv_name
        AND type = 'P'.

    IF sy-subrc = 0.
      " Entry exists - Update the LOW value
      UPDATE tvarvc
        SET low       = iv_value
            bitchangd = sy-datum     "Track last change date
        WHERE name = iv_name
          AND type = 'P'.

      IF sy-subrc <> 0.
        rv_ok = abap_false.
        log_to_application_log(
          iv_message = |Failed to UPDATE TVARVC parameter { iv_name }|
          iv_type    = 'E' ).
      ENDIF.

    ELSE.
      " Entry does not exist - Insert new
      CLEAR ls_tvarvc.
      ls_tvarvc-name      = iv_name.
      ls_tvarvc-type      = 'P'.
      ls_tvarvc-numb      = '0000'.
      ls_tvarvc-sign      = 'I'.
      ls_tvarvc-opti      = 'EQ'.
      ls_tvarvc-low       = iv_value.
      ls_tvarvc-bitchangd = sy-datum.

      INSERT tvarvc FROM ls_tvarvc.

      IF sy-subrc <> 0.
        rv_ok = abap_false.
        log_to_application_log(
          iv_message = |Failed to INSERT TVARVC parameter { iv_name }|
          iv_type    = 'E' ).
      ENDIF.

    ENDIF.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD update_tvarvc_range
* Updates or inserts a TVARVC Select-Option (Type S) entry with range
*----------------------------------------------------------------------*
  METHOD update_tvarvc_range.

    DATA: ls_tvarvc TYPE tvarvc.

    rv_ok = abap_true.

    " Delete all existing range entries for this variable
    DELETE FROM tvarvc
      WHERE name = iv_name
        AND type = 'S'.

    " Insert fresh range entry
    CLEAR ls_tvarvc.
    ls_tvarvc-name      = iv_name.
    ls_tvarvc-type      = 'S'.
    ls_tvarvc-numb      = '0000'.
    ls_tvarvc-sign      = 'I'.
    ls_tvarvc-opti      = 'BT'.        " BT = Between (range)
    ls_tvarvc-low       = iv_low.
    ls_tvarvc-high      = iv_high.
    ls_tvarvc-bitchangd = sy-datum.

    INSERT tvarvc FROM ls_tvarvc.

    IF sy-subrc <> 0.
      rv_ok = abap_false.
      log_to_application_log(
        iv_message = |Failed to INSERT TVARVC range { iv_name } ({ iv_low } - { iv_high })|
        iv_type    = 'E' ).
    ENDIF.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD write_all_tvarvc_entries
* Orchestrates writing all 5 TVARVC entries
*----------------------------------------------------------------------*
  METHOD write_all_tvarvc_entries.

    rv_ok = abap_true.

    "-- 1. Z_BPC_CATEGORY_FROM (Parameter)
    IF update_tvarvc_parameter(
         iv_name  = gc_tvar_cat_from
         iv_value = CONV #( ms_selections-category_from )
       ) = abap_false.
      rv_ok = abap_false.
      RETURN.
    ENDIF.

    "-- 2. Z_BPC_CATEGORY_TO (Parameter)
    IF update_tvarvc_parameter(
         iv_name  = gc_tvar_cat_to
         iv_value = CONV #( ms_selections-category_to )
       ) = abap_false.
      rv_ok = abap_false.
      RETURN.
    ENDIF.

    "-- 3. Z_BPC_TIME_FROM (Parameter)
    IF update_tvarvc_parameter(
         iv_name  = gc_tvar_time_from
         iv_value = CONV #( ms_selections-time_from )
       ) = abap_false.
      rv_ok = abap_false.
      RETURN.
    ENDIF.

    "-- 4. Z_BPC_TIME_TO (Parameter)
    IF update_tvarvc_parameter(
         iv_name  = gc_tvar_time_to
         iv_value = CONV #( ms_selections-time_to )
       ) = abap_false.
      rv_ok = abap_false.
      RETURN.
    ENDIF.

    "-- 5. Z_BPC_TIME_RANGE (Select-Option for DTP filter)
    IF update_tvarvc_range(
         iv_name = gc_tvar_time_range
         iv_low  = CONV #( ms_selections-time_from )
         iv_high = CONV #( ms_selections-time_to )
       ) = abap_false.
      rv_ok = abap_false.
      RETURN.
    ENDIF.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD add_message
* Adds a message to the BPC return message table (shown in DM log)
*----------------------------------------------------------------------*
  METHOD add_message.

    DATA: ls_message TYPE uj0_s_message.

    ls_message-severity = iv_type.     " I=Info, W=Warning, E=Error, S=Success
    ls_message-message  = iv_message.

    APPEND ls_message TO ct_message.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD log_to_application_log
* Writes to the SAP Application Log (SLG1) for audit/debugging
*----------------------------------------------------------------------*
  METHOD log_to_application_log.

    DATA: ls_log     TYPE bal_s_log,
          ls_msg     TYPE bal_s_msg,
          lv_log_handle TYPE balloghndl,
          lt_log_handle TYPE bal_t_logh.

    " Create log header
    ls_log-extnumber = 'Z_BPC_WRITE_TVAR'.
    ls_log-object    = 'UJ'.         " BPC log object
    ls_log-subobject = 'CUSTOM'.
    ls_log-aluser    = sy-uname.
    ls_log-alprog    = 'ZCL_BPC_WRITE_TVAR'.
    ls_log-aldate    = sy-datum.
    ls_log-altime    = sy-uzeit.

    CALL FUNCTION 'BAL_LOG_CREATE'
      EXPORTING
        i_s_log      = ls_log
      IMPORTING
        e_log_handle = lv_log_handle
      EXCEPTIONS
        OTHERS       = 1.

    IF sy-subrc = 0.
      " Add message
      ls_msg-msgty = iv_type.
      ls_msg-msgid = '00'.
      ls_msg-msgno = '001'.
      ls_msg-msgv1 = iv_message(50).
      IF strlen( iv_message ) > 50.
        ls_msg-msgv2 = iv_message+50.
      ENDIF.

      CALL FUNCTION 'BAL_LOG_MSG_ADD'
        EXPORTING
          i_log_handle = lv_log_handle
          i_s_msg      = ls_msg
        EXCEPTIONS
          OTHERS       = 1.

      " Save log
      APPEND lv_log_handle TO lt_log_handle.
      CALL FUNCTION 'BAL_DB_SAVE'
        EXPORTING
          i_t_log_handle = lt_log_handle
        EXCEPTIONS
          OTHERS         = 1.
    ENDIF.

  ENDMETHOD.

ENDCLASS.
```

### 3.2 Type Definition Reference: UJK_T_SCRIPT_LOGIC_HASHTABLE

The `IT_PARAM` parameter uses type `UJK_T_SCRIPT_LOGIC_HASHTABLE`. This is a standard BPC type:

```
Table Type : UJK_T_SCRIPT_LOGIC_HASHTABLE
Line Type  : UJK_S_SCRIPT_LOGIC_HASHTABLE

Structure fields:
  HASHTABLE_KEY   TYPE STRING   " Parameter name (e.g., 'CATEGORY_FROM')
  HASHTABLE_VALUE TYPE STRING   " Parameter value (e.g., 'ACTUAL')
```

> **Important**: In some BPC versions, the parameter names may use fields `NAME` and `VALUE` instead of `HASHTABLE_KEY` and `HASHTABLE_VALUE`. Check your system's type definition in **SE11**.

### 3.3 Adjust for Your BPC Version

If your BPC version uses different field names in `IT_PARAM`, modify the `parse_parameters` method:

```abap
  " For BPC 10.0 (older field names):
  LOOP AT it_param INTO ls_param.
    DATA(lv_name)  = to_upper( ls_param-name ).       " instead of hashtable_key
    DATA(lv_value) = ls_param-value.                   " instead of hashtable_value
    ...

  " For BPC 10.1 (newer field names):
  LOOP AT it_param INTO ls_param.
    DATA(lv_name)  = to_upper( ls_param-hashtable_key ).
    DATA(lv_value) = ls_param-hashtable_value.
    ...
```

Check your system: **SE11** > Data Type `UJK_S_SCRIPT_LOGIC_HASHTABLE` > Display fields.

---

## 4. Complete BADI Class Code - UJO_BADI_DM_PACKAGE (Alternative)

This is the **alternative approach** using the Data Manager Package BADI. Use this if you want to intercept the Data Manager execution directly (without Script Logic).

### 4.1 Create Enhancement Implementation for UJO_BADI_DM_PACKAGE

| Field | Value |
|-------|-------|
| Transaction | SE19 |
| Enhancement Spot | `UJO_ES_DM_PACKAGE` |
| BADI Definition | `UJO_BADI_DM_PACKAGE` |
| Enhancement Impl. | `Z_EI_DM_TVAR` |
| BADI Impl. | `Z_BI_DM_WRITE_TVAR` |
| Implementing Class | `ZCL_BPC_DM_WRITE_TVAR` |
| Filter Value | `Z_COPY_ACTUAL_TO_FCST` (your package ID) |

### 4.2 Complete Class Code

```abap
*----------------------------------------------------------------------*
* Class ZCL_BPC_DM_WRITE_TVAR
* BADI Implementation for UJO_BADI_DM_PACKAGE
* Purpose: Intercepts BPC Data Manager package execution,
*          reads user prompt selections, writes to TVARVC.
*
* Enhancement Spot : UJO_ES_DM_PACKAGE
* BADI Definition  : UJO_BADI_DM_PACKAGE
* Interface        : IF_UJO_DM_PACKAGE
* Filter           : Package ID (Z_COPY_ACTUAL_TO_FCST)
*----------------------------------------------------------------------*
CLASS zcl_bpc_dm_write_tvar DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.

    INTERFACES if_badi_interface.
    INTERFACES if_ujo_dm_package.

    CONSTANTS:
      gc_tvar_cat_from   TYPE tvarvc-name VALUE 'Z_BPC_CATEGORY_FROM',
      gc_tvar_cat_to     TYPE tvarvc-name VALUE 'Z_BPC_CATEGORY_TO',
      gc_tvar_time_from  TYPE tvarvc-name VALUE 'Z_BPC_TIME_FROM',
      gc_tvar_time_to    TYPE tvarvc-name VALUE 'Z_BPC_TIME_TO',
      gc_tvar_time_range TYPE tvarvc-name VALUE 'Z_BPC_TIME_RANGE'.

  PROTECTED SECTION.
  PRIVATE SECTION.

    METHODS update_tvarvc_param
      IMPORTING iv_name  TYPE tvarvc-name
                iv_value TYPE clike.

    METHODS update_tvarvc_range
      IMPORTING iv_name TYPE tvarvc-name
                iv_low  TYPE clike
                iv_high TYPE clike.

ENDCLASS.


CLASS zcl_bpc_dm_write_tvar IMPLEMENTATION.

*----------------------------------------------------------------------*
* METHOD if_ujo_dm_package~pre_process
* Called BEFORE the Data Manager package runs.
* This is where we capture user selections and write to TVARVC.
*----------------------------------------------------------------------*
  METHOD if_ujo_dm_package~pre_process.

    DATA: lv_cat_from  TYPE string,
          lv_cat_to    TYPE string,
          lv_time_from TYPE string,
          lv_time_to   TYPE string.

    " IT_PARAM_VALUE contains all user prompt selections
    " Each entry has:
    "   PARAM_NAME  = Prompt variable name (e.g., 'CATEGORY_FROM')
    "   PARAM_VALUE = User-entered value (e.g., 'ACTUAL')

    LOOP AT it_param_value INTO DATA(ls_param).
      CASE ls_param-param_name.
        WHEN 'CATEGORY_FROM'.
          lv_cat_from = ls_param-param_value.
        WHEN 'CATEGORY_TO'.
          lv_cat_to = ls_param-param_value.
        WHEN 'TIME_FROM'.
          lv_time_from = ls_param-param_value.
        WHEN 'TIME_TO'.
          lv_time_to = ls_param-param_value.
      ENDCASE.
    ENDLOOP.

    " Validate
    IF lv_cat_from IS INITIAL OR lv_cat_to IS INITIAL OR
       lv_time_from IS INITIAL OR lv_time_to IS INITIAL.
      " Return error - missing parameters
      DATA(ls_msg) = VALUE uj0_s_message(
        severity = 'E'
        message  = 'Missing selection parameters. Provide CATEGORY_FROM, CATEGORY_TO, TIME_FROM, TIME_TO.' ).
      APPEND ls_msg TO et_message.
      ev_flag = abap_false.
      RETURN.
    ENDIF.

    " Acquire lock
    CALL FUNCTION 'ENQUEUE_E_TABLE'
      EXPORTING
        tabname  = 'TVARVC'
        varkey   = 'Z_BPC_%'
        _wait    = 'X'
      EXCEPTIONS
        foreign_lock = 1
        OTHERS       = 2.

    IF sy-subrc <> 0.
      APPEND VALUE uj0_s_message(
        severity = 'E'
        message  = |Lock on TVARVC failed. Another user may be running the process.| )
        TO et_message.
      ev_flag = abap_false.
      RETURN.
    ENDIF.

    " Write to TVARVC
    update_tvarvc_param( iv_name = gc_tvar_cat_from   iv_value = lv_cat_from ).
    update_tvarvc_param( iv_name = gc_tvar_cat_to     iv_value = lv_cat_to ).
    update_tvarvc_param( iv_name = gc_tvar_time_from  iv_value = lv_time_from ).
    update_tvarvc_param( iv_name = gc_tvar_time_to    iv_value = lv_time_to ).
    update_tvarvc_range( iv_name = gc_tvar_time_range iv_low = lv_time_from iv_high = lv_time_to ).

    COMMIT WORK AND WAIT.

    " Release lock
    CALL FUNCTION 'DEQUEUE_E_TABLE'
      EXPORTING
        tabname = 'TVARVC'
        varkey  = 'Z_BPC_%'.

    " Return success messages
    APPEND VALUE uj0_s_message(
      severity = 'S'
      message  = |TVARVC updated: { lv_cat_from } -> { lv_cat_to }, Time { lv_time_from } - { lv_time_to }| )
      TO et_message.

    ev_flag = abap_true.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD if_ujo_dm_package~post_process
* Called AFTER the Data Manager package runs.
* Use for cleanup, logging, or notification.
*----------------------------------------------------------------------*
  METHOD if_ujo_dm_package~post_process.

    " Optional: Log completion, send notification, etc.
    APPEND VALUE uj0_s_message(
      severity = 'S'
      message  = |Data Manager package completed successfully.| )
      TO et_message.

    ev_flag = abap_true.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD update_tvarvc_param
*----------------------------------------------------------------------*
  METHOD update_tvarvc_param.

    DATA: ls_tvarvc TYPE tvarvc.

    SELECT SINGLE * FROM tvarvc INTO ls_tvarvc
      WHERE name = iv_name AND type = 'P'.

    IF sy-subrc = 0.
      UPDATE tvarvc SET low = iv_value
        WHERE name = iv_name AND type = 'P'.
    ELSE.
      CLEAR ls_tvarvc.
      ls_tvarvc-name = iv_name.
      ls_tvarvc-type = 'P'.
      ls_tvarvc-numb = '0000'.
      ls_tvarvc-sign = 'I'.
      ls_tvarvc-opti = 'EQ'.
      ls_tvarvc-low  = iv_value.
      INSERT tvarvc FROM ls_tvarvc.
    ENDIF.

  ENDMETHOD.


*----------------------------------------------------------------------*
* METHOD update_tvarvc_range
*----------------------------------------------------------------------*
  METHOD update_tvarvc_range.

    DATA: ls_tvarvc TYPE tvarvc.

    DELETE FROM tvarvc WHERE name = iv_name AND type = 'S'.

    CLEAR ls_tvarvc.
    ls_tvarvc-name = iv_name.
    ls_tvarvc-type = 'S'.
    ls_tvarvc-numb = '0000'.
    ls_tvarvc-sign = 'I'.
    ls_tvarvc-opti = 'BT'.
    ls_tvarvc-low  = iv_low.
    ls_tvarvc-high = iv_high.
    INSERT tvarvc FROM ls_tvarvc.

  ENDMETHOD.

ENDCLASS.
```

### 4.3 Interface Method Signatures for IF_UJO_DM_PACKAGE

```
+------------------------------------------------------------------+
| Interface: IF_UJO_DM_PACKAGE                                     |
|------------------------------------------------------------------|
|                                                                  |
| Method: PRE_PROCESS                                              |
|   IMPORTING:                                                     |
|     IV_APPSET_ID    TYPE UJ_APPSET_ID    (AppSet name)          |
|     IV_APPL_ID      TYPE UJ_APPL_ID      (Application name)    |
|     IV_PACKAGE_ID   TYPE UJO_PACKAGE_ID   (DM Package ID)       |
|     IT_PARAM_VALUE  TYPE UJO_T_PARAM_VALUE (User selections)    |
|   EXPORTING:                                                     |
|     ET_MESSAGE      TYPE UJ0_T_MESSAGE    (Return messages)     |
|     EV_FLAG         TYPE UJ_FLG           (Success flag)        |
|                                                                  |
| Method: POST_PROCESS                                             |
|   IMPORTING:                                                     |
|     IV_APPSET_ID    TYPE UJ_APPSET_ID                           |
|     IV_APPL_ID      TYPE UJ_APPL_ID                             |
|     IV_PACKAGE_ID   TYPE UJO_PACKAGE_ID                          |
|     IT_PARAM_VALUE  TYPE UJO_T_PARAM_VALUE                      |
|   EXPORTING:                                                     |
|     ET_MESSAGE      TYPE UJ0_T_MESSAGE                          |
|     EV_FLAG         TYPE UJ_FLG                                 |
+------------------------------------------------------------------+
```

---

## 5. Script Logic File to Trigger BADI (For Approach A only)

### 5.1 Create the Script Logic File

In BPC Administration, create a Script Logic file that will call the BADI:

**File Path**: `<AppSet>/<Application>/Logic/Z_WRITE_TVAR_LOGIC.lgf`

```
*SCRIPT_LOGIC
*XDIM_MEMBERSET CATEGORY = %CATEGORY_FROM_SET%
*XDIM_MEMBERSET TIME = %TIME_FROM_SET%,%TIME_TO_SET%

*START_BADI Z_WRITE_TVAR
  CATEGORY_FROM = %CATEGORY_FROM_SET%
  CATEGORY_TO   = %CATEGORY_TO_SET%
  TIME_FROM     = %TIME_FROM_SET%
  TIME_TO       = %TIME_TO_SET%
*END_BADI
```

> **Note**: The `%VARIABLE%` tokens are replaced at runtime by the Data Manager prompt values.

### 5.2 Alternative Script Logic Syntax (BPC 10.1)

In BPC NW 10.1, the syntax to call a custom BADI function is:

```
*RUNLOGIC
*FUNCTION Z_WRITE_TVAR
*CATEGORY_FROM=%CATEGORY_FROM%
*CATEGORY_TO=%CATEGORY_TO%
*TIME_FROM=%TIME_FROM%
*TIME_TO=%TIME_TO%
*ENDRUNLOGIC
```

**Critical**: The value `Z_WRITE_TVAR` after `*FUNCTION` must match the **filter value** you set in Step 2.6.

### 5.3 Data Manager Package Script Logic Tab

In the BPC Data Manager package, go to the **"Script"** tab and link to this logic file:

```
+------------------------------------------------------------------+
|  Data Manager Package: Z_COPY_ACTUAL_TO_FCST                    |
|  Tab: Script Logic                                               |
|------------------------------------------------------------------|
|                                                                  |
|  Script Logic File: Z_WRITE_TVAR_LOGIC.lgf                      |
|                                                                  |
|  Dynamic Script:                                                 |
|  +------------------------------------------------------------+ |
|  | *RUNLOGIC                                                   | |
|  | *FUNCTION Z_WRITE_TVAR                                      | |
|  | *CATEGORY_FROM=%CATEGORY_FROM%                              | |
|  | *CATEGORY_TO=%CATEGORY_TO%                                  | |
|  | *TIME_FROM=%TIME_FROM%                                      | |
|  | *TIME_TO=%TIME_TO%                                          | |
|  | *ENDRUNLOGIC                                                | |
|  +------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

The `%CATEGORY_FROM%` tokens reference the prompt variable names defined in Step 1.3 of the main solution document.

---

## 6. Data Manager Package Configuration

### 6.1 Complete Package Setup Summary

```
+==================================================================+
|  DATA MANAGER PACKAGE CONFIGURATION                              |
|==================================================================|
|                                                                  |
|  GENERAL TAB                                                     |
|  +---------------------------------------------------------+    |
|  | Package ID   : Z_COPY_ACTUAL_TO_FCST                    |    |
|  | Description  : Copy Actual to Forecast with Selections  |    |
|  | Team         : ADMIN                                    |    |
|  | Package Type : Script Logic    <-- for BADI Approach A  |    |
|  |            OR: Process Chain   <-- for Approach B       |    |
|  +---------------------------------------------------------+    |
|                                                                  |
|  PROMPT TAB                                                      |
|  +---------------------------------------------------------+    |
|  | Variable       | Dimension | Type    | Default          |    |
|  |----------------|-----------|---------|------------------|    |
|  | CATEGORY_FROM  | CATEGORY  | Single  | ACTUAL           |    |
|  | CATEGORY_TO    | CATEGORY  | Single  | FEB_FCST         |    |
|  | TIME_FROM      | TIME      | Single  | 2026.01          |    |
|  | TIME_TO        | TIME      | Single  | 2026.12          |    |
|  +---------------------------------------------------------+    |
|                                                                  |
|  SCRIPT TAB (Approach A - Script Logic)                          |
|  +---------------------------------------------------------+    |
|  | *RUNLOGIC                                                |    |
|  | *FUNCTION Z_WRITE_TVAR                                   |    |
|  | *CATEGORY_FROM=%CATEGORY_FROM%                           |    |
|  | *CATEGORY_TO=%CATEGORY_TO%                               |    |
|  | *TIME_FROM=%TIME_FROM%                                   |    |
|  | *TIME_TO=%TIME_TO%                                       |    |
|  | *ENDRUNLOGIC                                             |    |
|  +---------------------------------------------------------+    |
|                                                                  |
|  PROCESS CHAIN TAB (Approach B - Process Chain)                  |
|  +---------------------------------------------------------+    |
|  | Process Chain : Z_PC_BPC_COPY_ACTUAL_FCST                |    |
|  | Steps:                                                   |    |
|  |   1. ABAP Program (writes TVAR)                         |    |
|  |   2. DTP Execution (reads TVAR, copies data)            |    |
|  +---------------------------------------------------------+    |
|                                                                  |
+==================================================================+
```

### 6.2 Choosing Between Approach A and B

| Criteria | Approach A (UJ_CUSTOM_LOGIC) | Approach B (UJO_BADI_DM_PACKAGE) |
|----------|------------------------------|----------------------------------|
| Package Type | Script Logic | Process Chain |
| BADI | UJ_CUSTOM_LOGIC | UJO_BADI_DM_PACKAGE |
| DTP Trigger | Separate (manual or via separate process chain) | Built into the process chain step |
| Complexity | Simpler (BADI writes TVAR, then separately run DTP) | More integrated (BADI + DTP in one chain) |
| Best For | When TVAR write and DTP are in different process chains | When everything runs in a single process chain |
| Concurrency | Need to handle externally | Easier to serialize |

**Recommendation**: For end-to-end automation (user clicks Run and everything happens), use **Approach B** (Process Chain with UJO_BADI_DM_PACKAGE or ABAP program in chain).

For **maximum flexibility** where the BADI writes TVAR and a separate job/chain runs the DTP, use **Approach A** (UJ_CUSTOM_LOGIC).

---

## 7. Testing and Debugging

### 7.1 Test BADI in Isolation (SE24)

1. Open **SE24** > Class `ZCL_BPC_WRITE_TVAR`
2. Click **"Test"** (F8) - this opens the Test Environment
3. You cannot directly test a BADI class via SE24 Test because it requires the BPC context. Instead, use Step 7.2.

### 7.2 Test via ABAP Test Program (SE38)

Create a test report to simulate what the Script Logic engine does:

```abap
*&---------------------------------------------------------------------*
*& Report Z_TEST_BADI_BPC_TVAR
*& Test program for BADI ZCL_BPC_WRITE_TVAR
*&---------------------------------------------------------------------*
REPORT z_test_badi_bpc_tvar.

DATA: lo_badi     TYPE REF TO zcl_bpc_write_tvar,
      lt_param    TYPE ujk_t_script_logic_hashtable,
      ls_param    TYPE ujk_s_script_logic_hashtable,
      lt_messages TYPE uj0_t_message,
      lv_flag     TYPE uj_flg,
      lr_data     TYPE REF TO data.

PARAMETERS: p_catfr  TYPE char30 DEFAULT 'ACTUAL'   OBLIGATORY,
            p_catto  TYPE char30 DEFAULT 'FEB_FCST' OBLIGATORY,
            p_timefr TYPE char30 DEFAULT '2026.01'  OBLIGATORY,
            p_timeto TYPE char30 DEFAULT '2026.12'  OBLIGATORY.

START-OF-SELECTION.

  " Build parameter table (simulating Script Logic)
  CLEAR ls_param.
  ls_param-hashtable_key   = 'CATEGORY_FROM'.
  ls_param-hashtable_value = p_catfr.
  APPEND ls_param TO lt_param.

  CLEAR ls_param.
  ls_param-hashtable_key   = 'CATEGORY_TO'.
  ls_param-hashtable_value = p_catto.
  APPEND ls_param TO lt_param.

  CLEAR ls_param.
  ls_param-hashtable_key   = 'TIME_FROM'.
  ls_param-hashtable_value = p_timefr.
  APPEND ls_param TO lt_param.

  CLEAR ls_param.
  ls_param-hashtable_key   = 'TIME_TO'.
  ls_param-hashtable_value = p_timeto.
  APPEND ls_param TO lt_param.

  " Create BADI instance and call execute
  CREATE OBJECT lo_badi.

  lo_badi->if_uj_custom_logic~execute(
    EXPORTING
      it_param   = lt_param
      it_data    = lr_data
      io_caller  = VALUE #( )       "No context in test mode
    CHANGING
      ct_data    = lr_data
    IMPORTING
      et_message = lt_messages
      ev_flag    = lv_flag ).

  " Display results
  WRITE: / 'Return Flag:', lv_flag.
  WRITE: / ''.
  WRITE: / 'Messages:'.
  WRITE: / '---------'.
  LOOP AT lt_messages INTO DATA(ls_msg).
    WRITE: / ls_msg-severity, ':', ls_msg-message.
  ENDLOOP.

  " Verify TVARVC entries
  WRITE: / ''.
  WRITE: / 'TVARVC Verification:'.
  WRITE: / '--------------------'.

  DATA: ls_tvarvc TYPE tvarvc.
  SELECT * FROM tvarvc INTO ls_tvarvc WHERE name LIKE 'Z_BPC_%'.
    WRITE: / ls_tvarvc-name, ls_tvarvc-type, ls_tvarvc-opti,
             ls_tvarvc-low, ls_tvarvc-high.
  ENDSELECT.
```

### 7.3 Debugging with Breakpoints

1. Open **SE24** > Class `ZCL_BPC_WRITE_TVAR`
2. Navigate to method `IF_UJ_CUSTOM_LOGIC~EXECUTE`
3. Set an **external breakpoint** (Ctrl+Shift+F12) on the first line
4. Run the Data Manager package from BPC
5. The debugger will stop at your breakpoint

**Important**: For external breakpoints to work, ensure your user is set in **Debugging** settings:
- Transaction **SM50** > your user > Debugging enabled
- Or set in **SE38** > Utilities > Settings > ABAP Editor > Debugging

### 7.4 Check Application Log (SLG1)

1. Open transaction **SLG1**
2. Enter filter:
   - Object: `UJ`
   - Subobject: `CUSTOM`
   - External ID: `Z_BPC_WRITE_TVAR`
   - Date: Today
3. Click **Execute**
4. Review all log messages from the BADI execution

### 7.5 Verify TVARVC Entries (STVARV)

1. Open transaction **STVARV** (or **SM30** with view `TVARVC`)
2. Search for entries with name `Z_BPC_*`
3. Verify the values match what was entered in the Data Manager prompts:

```
Expected after test run:
+------------------------+------+------+------+-----------+-----------+
| NAME                   | TYPE | SIGN | OPTI | LOW       | HIGH      |
+------------------------+------+------+------+-----------+-----------+
| Z_BPC_CATEGORY_FROM    | P    | I    | EQ   | ACTUAL    |           |
| Z_BPC_CATEGORY_TO      | P    | I    | EQ   | FEB_FCST  |           |
| Z_BPC_TIME_FROM        | P    | I    | EQ   | 2026.01   |           |
| Z_BPC_TIME_TO          | P    | I    | EQ   | 2026.12   |           |
| Z_BPC_TIME_RANGE       | S    | I    | BT   | 2026.01   | 2026.12   |
+------------------------+------+------+------+-----------+-----------+
```

### 7.6 Common Errors and Fixes

| Error | Symptom | Fix |
|-------|---------|-----|
| BADI not called | No breakpoint hit, no TVARVC update | Check filter value matches `*FUNCTION` name in Script Logic |
| `CX_SY_REF_IS_INITIAL` dump | io_caller is null | Add `IF io_caller IS BOUND` check (already in our code) |
| TVARVC not updated | Values remain old | Check COMMIT WORK is called; check authorization for TVARVC |
| `TABLE_NOT_LOCKED` | Enqueue fails | Check lock object E_TABLE exists (standard SAP) |
| Wrong parameter values | All blank | Check IT_PARAM field names (hashtable_key vs name) - see Section 3.3 |
| Script Logic error | "Function Z_WRITE_TVAR not found" | Enhancement Implementation not active; activate in SE19 |
| Authorization dump | `AUTHORITY_CHECK` failure | Assign auth object S_TABU_DIS with activity 02 for table TVARVC |

---

## 8. Appendix

### 8.1 Complete Object Checklist

| # | Object Type | Name | Transaction | Status |
|---|-------------|------|-------------|--------|
| 1 | Enhancement Spot | UJ_ES_CUSTOM_LOGIC | SE18 (display) | SAP Standard |
| 2 | BADI Definition | UJ_CUSTOM_LOGIC | SE18 (display) | SAP Standard |
| 3 | Enhancement Implementation | Z_EI_BPC_WRITE_TVAR | SE19 | Custom - Create |
| 4 | BADI Implementation | Z_BI_BPC_WRITE_TVAR | SE19 | Custom - Create |
| 5 | ABAP Class | ZCL_BPC_WRITE_TVAR | SE24 | Custom - Create |
| 6 | Filter Value | Z_WRITE_TVAR | SE19 (in BADI Impl.) | Custom - Configure |
| 7 | TVARVC Variables | Z_BPC_CATEGORY_FROM, etc. | STVARV/SM30 | Custom - Create |
| 8 | Script Logic File | Z_WRITE_TVAR_LOGIC.lgf | BPC Admin | Custom - Create |
| 9 | DM Package | Z_COPY_ACTUAL_TO_FCST | BPC Data Manager | Custom - Create |
| 10 | Test Program | Z_TEST_BADI_BPC_TVAR | SE38 | Custom - Create |

### 8.2 Transport Request Objects

When creating the transport request, include:

```
R3TR  ENHS  Z_EI_BPC_WRITE_TVAR      (Enhancement Implementation)
R3TR  CLAS  ZCL_BPC_WRITE_TVAR        (ABAP Class)
R3TR  PROG  Z_TEST_BADI_BPC_TVAR      (Test Program - DEV only)
```

> TVARVC entries are **client-dependent** and must be maintained in each client/system separately via STVARV.

### 8.3 Decision Matrix: SE18 vs SE19

| Transaction | Purpose | When to Use |
|------------|---------|-------------|
| **SE18** | BADI **Definition** - View the BADI definition, interface, filter type | To understand the BADI (read-only for SAP standard) |
| **SE19** | BADI **Implementation** - Create your custom implementation | To create and activate your BADI implementation |
| **SE24** | Class Builder - Edit the implementing class | To write/debug the ABAP class code |
| **SE11** | Data Dictionary - View types/structures | To check parameter types like UJK_S_SCRIPT_LOGIC_HASHTABLE |
