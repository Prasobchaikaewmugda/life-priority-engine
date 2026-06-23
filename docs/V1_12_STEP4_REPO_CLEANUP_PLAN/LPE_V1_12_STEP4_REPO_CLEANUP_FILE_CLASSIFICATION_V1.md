# LPE V1.12 Step 4 — Repo Cleanup File Classification V1

| Status | Path | Category | Safe Default Action |
|---|---|---|---|
| M | `README.md` | COMMIT_CANDIDATE_CORE_RELEASE | stage later only after final gate review |
| M | `requirements.txt` | COMMIT_CANDIDATE_CORE_RELEASE | stage later only after final gate review |
| ?? | `docs/00_LIFE_PRIORITY_ENGINE_MASTER_PROJECT_MAP_V1.md` | REVIEW_CANONICAL_DOC_MAY_COMMIT | review content then decide |
| ?? | `docs/01_LIFE_PRIORITY_ENGINE_CODEX_WORKFLOW_AND_GATE_ROADMAP_V1.md` | REVIEW_CANONICAL_DOC_MAY_COMMIT | review content then decide |
| ?? | `docs/02_LIFE_PRIORITY_ENGINE_RULES_V1.md` | REVIEW_CANONICAL_DOC_MAY_COMMIT | review content then decide |
| ?? | `docs/ACCEPTANCE_RECORDS/` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `docs/CODEX_SUPPORT/` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `docs/DEPLOYMENT_PREP/` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `docs/GITHUB_PACKAGING/` | REVIEW_OLD_PHASE_DOCS_NOT_CORE_RELEASE | review/possibly archive; not core release |
| ?? | `docs/GITHUB_PUSH_EXECUTION/` | REVIEW_OLD_PHASE_DOCS_NOT_CORE_RELEASE | review/possibly archive; not core release |
| ?? | `docs/GITHUB_PUSH_PREP/` | REVIEW_OLD_PHASE_DOCS_NOT_CORE_RELEASE | review/possibly archive; not core release |
| ?? | `docs/LPE_V1_10B_LAYERED_SCRIPT_RUNBOOK_V1.txt` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `docs/PUBLIC_DEMO_HARDENING/` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `docs/STREAMLIT_DEPLOY_PREP/` | REVIEW_OLD_PHASE_DOCS_NOT_CORE_RELEASE | review/possibly archive; not core release |
| ?? | `docs/STREAMLIT_DEPLOY_VERIFY/` | REVIEW_OLD_PHASE_DOCS_NOT_CORE_RELEASE | review/possibly archive; not core release |
| ?? | `docs/V1_11_STEP1_LIFE_SETTINGS/` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `docs/V1_12_STEP1_PROJECT_COMPLETION_SCOPE_AUDIT/` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `docs/V1_12_STEP2_PROJECT_COMPLETION_AUDIT_REPORT/` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `docs/V1_12_STEP3_README_REQUIREMENTS_USER_GUIDE/` | REVIEW_DOCS_NOT_CLASSIFIED | manual review |
| ?? | `prototypes/` | REVIEW_UNKNOWN | manual review |
| ?? | `scripts/LPE_SUPREME_MASTER_PROJECT_BLUEPRINT_V1.md` | REVIEW_SCRIPT_DOC_ARTIFACT | review before any commit |
| ?? | `scripts/LPE_V1_11_STEP1B_HOW_TO_USE_SCHEMA_DESIGN_V1.txt` | REVIEW_SCRIPT_DOC_ARTIFACT | review before any commit |
| ?? | `scripts/LPE_V1_11_STEP1B_LIFE_PROFILE_SCHEMA_DESIGN_V1.md` | REVIEW_SCRIPT_DOC_ARTIFACT | review before any commit |
| ?? | `scripts/LPE_V1_11_STEP1B_LIFE_PROFILE_SCHEMA_V1.json` | REVIEW_SCRIPT_DOC_ARTIFACT | review before any commit |
| ?? | `scripts/run_lpe_v1_10_codex_support_packet_and_local_ux_audit_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_10b_1_mobile_usability_rescue_fixed_runner_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_10b_2_session_state_hotfix_commit_push_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_10b_3_navigation_state_readability_stabilization_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_10b_git_commit_push_guarded_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_10b_next_step_router_read_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step10_commit_only_gate_no_push_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step10a_commit_only_gate_secret_scan_classifier_fix_no_push_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step10b_commit_only_gate_secret_scan_gitignore_allow_no_push_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step11_push_gate_remote_verify_then_push_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step12_streamlit_deployment_verify_gate_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1a_life_settings_scope_audit_read_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1b_2_master_blueprint_install_design_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1b_life_profile_schema_design_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1c_2_1_settings_navigation_route_hotfix_local_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1c_2_2_settings_readability_stacked_ux_hotfix_local_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1c_2_2a_settings_readability_patch_verify_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1c_2_3_settings_clean_readable_ux_hotfix_local_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1c_2_3_settings_clean_readable_ux_hotfix_local_only_v2.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1c_2_five_mode_life_story_settings_patch_local_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step1c_settings_form_patch_local_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step2_1_nav_and_next_action_ux_hotfix_local_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step2_2_global_readability_hard_reset_local_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step2_3_clean_consolidation_static_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step2_3a_clean_consolidation_verify_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step2_daily_checkin_patch_local_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step3_1_daily_plan_engine_patch_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step3_daily_plan_engine_blueprint_design_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step4_1_task_result_daily_reflection_patch_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step4_task_result_daily_reflection_blueprint_design_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step5_1_json_persistence_patch_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step5_json_persistence_blueprint_design_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_1_completion_label_collision_hotfix_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_2_autosave_and_guided_questions_hotfix_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_2a_autosave_indent_repair_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_2b_guided_questions_key_compat_hotfix_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_2c_guided_questions_key_compat_hotfix_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_2d_placeholder_key_compat_hotfix_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_2e_used_for_key_compat_hotfix_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_3_product_flow_cleanup_hotfix_local_only_no_web_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step6_product_flow_audit_static_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step7_release_readiness_audit_static_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step8_commit_preparation_gate_static_only_no_commit_no_push_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_11_step9_guarded_staging_gate_no_commit_no_push_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_12_step1_project_completion_scope_audit_design_only_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_12_step2_project_completion_audit_report_patch_no_app_mutation_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_12_step3_readme_requirements_user_guide_patch_no_app_mutation_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_12_step4_repo_cleanup_plan_static_only_no_delete_no_commit_no_push_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_2_thai_dashboard_acceptance_record_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_3_deployment_preparation_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_4_github_repository_packaging_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_5_1_github_push_preparation_report_fix_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_5_github_push_preparation_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_6_1_invalid_gitdir_repair_and_github_push_execution_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_6_github_init_add_commit_push_execution_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_7_1_streamlit_deploy_prep_report_fix_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_7_streamlit_cloud_deployment_preparation_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_8_1_streamlit_post_deployment_verification_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_8_2_streamlit_post_deployment_verification_redirect_tolerant_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
| ?? | `scripts/run_lpe_v1_9_public_demo_hardening_mobile_first_ux_v1.sh` | LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | keep local runner archive; do not commit by default |
