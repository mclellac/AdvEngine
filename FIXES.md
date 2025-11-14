# AdvEngine Stability Audit and Fixes

## 1. Introduction

This document outlines the findings of a complete audit of the AdvEngine
application. The audit was conducted to identify the root causes of the
instability, bugs, and crashes that have been plaguing the application,
particularly the critical failure during the "New Project" workflow.

The audit has confirmed that the recent instability is a direct result of
critical violations of the project's own documented design standards and the
correct usage of the GTK and Libadwaita libraries. The application's core
architecture, as defined in `docs/design`, is sound, but the implementation
has deviated from these principles.

This document will detail the specific violations found and provide a clear,
actionable plan to fix them. **No code changes have been made.** This document
is the sole output of the audit.

## 2. Critical Issues Found

The following critical issues were identified as the primary causes of the
application's instability.

### 2.1. `Adw.Dialog` Implementation Violations

The most severe issues stem from the incorrect implementation of `Adw.Dialog`
subclasses, which directly contradicts the explicit instructions in
`AGENTS.md`. These are not minor bugs; they are fundamental errors that cause
the GTK template system to fail, leading to crashes.

#### 2.1.1. Invalid `title` Property in `new_project_dialog.ui`

*   **File:** `src/ui/new_project_dialog.ui`
*   **Problem:** The file attempts to set the dialog's title using
    `<property name="title">Create a New Project</property>`. The `Adw.Dialog`
    widget does not have a `title` property. This is an invalid property and
    causes a critical error during the parsing of the UI file. When GtkBuilder
    encounters this error, it aborts the creation of the widget, meaning the
    `NewProjectDialog` is never properly instantiated. Any attempt to use it
    will result in a crash.
*   **Fix:**
    1.  Remove the `<property name="title">` line entirely from
        `src/ui/new_project_dialog.ui`.
    2.  To set the title correctly, add a `title` property to the
        `Adw.HeaderBar` that is already present in the UI file. The corrected
        header bar should look like this:

        ```xml
        <object class="AdwHeaderBar">
          <property name="title-widget">
            <object class="AdwWindowTitle">
              <property name="title">Create a New Project</property>
            </object>
          </property>
          <child type="start">
            ...
          </child>
          ...
        </object>
        ```

### 2.1.2. Incorrect `destroy()` Method Call on `Adw.MessageDialog`

*   **File:** `src/main.py`
*   **Method:** `EditorWindow.on_error`
*   **Problem:** The error dialog handler is implemented as
    `dialog.connect("response", lambda d, r: d.destroy())`. The
    `Adw.MessageDialog` widget, like `Adw.Dialog`, does not have a `destroy()`
    method. It has a `close()` method. Calling `destroy()` will cause an
    `AttributeError` and crash the application every time an error dialog is
    shown.
*   **Fix:**
    1.  In `src/main.py`, change the `on_error` method's signal connection to
        use `close()` instead of `destroy()`. The corrected line should be:

        ```python
        dialog.connect("response", lambda d, r: d.close())
        ```

## 3. General Code Quality and Consistency Issues

While the above issues are the primary drivers of the crashes, the audit also
revealed several areas where the code quality and consistency could be
improved to prevent future bugs.

### 3.1. Inconsistent Signal Handling in `main.py`

*   **File:** `src/main.py`
*   **Method:** `AdvEngine.on_new_project_activate`
*   **Problem:** The `response` signal for the `NewProjectDialog` is connected,
    but the dialog is not closed in the `cancel` case. While not a crash, this
    leaves the dialog hanging and is inconsistent with the expected behavior.
*   **Fix:**
    1.  The `on_response` function should be simplified to handle both the
        `create` and `cancel` cases explicitly, and the dialog should always be
        closed.

        ```python
        def on_response(dialog, response_id):
            if response_id == "create":
                # ... (rest of the logic)
            dialog.close()
        ```

### 3.2. Adherence to GNOME HIG

The use of `Adw.PreferencesPage` and `Adw.PreferencesGroup` within the
`NewProjectDialog` is good and follows the GNOME Human Interface Guidelines.
This pattern should be consistently applied across all dialogs and editor
views to ensure a uniform user experience.

## 4. Recommendations for a Path to Stability

1.  **Immediate Fixes:** The two critical issues identified in section 2 must
    be fixed immediately. These are the direct cause of the crashes and the
    application will not be usable until they are resolved.
2.  **Full Code Review:** A full review of all UI files and their corresponding
    Python modules should be conducted to ensure that all widget usage conforms
    to the GTK4 and Libadwaita 1.8 APIs. The `AGENTS.md` file should be used as
    a checklist during this review.
3.  **Establish a Testing Protocol:** While a full automated test suite is a
    long-term goal, a simple, manual "smoke test" protocol should be
    established and run before any new changes are submitted. This protocol
    should include:
    *   Starting the application.
    *   Creating a new project from a template.
    *   Opening an existing project.
    *   Verifying that all editor modules load without errors.
    *   Saving the project.

By following these recommendations, the application can be quickly returned to a
stable state, and future regressions can be prevented.
