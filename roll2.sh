#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  OpenRoot Rollout · phone (Termux) → optiplex
#  generated : 2026-11-11T01:16:04.987Z
#  payload   : 2148 files · 18.8 MB · 2148 manifest hashes
#  symlinks  : 19 (manual checklist below — targets are device-specific)
#  usage     : TARGET=<ssh-alias> bash openroot-rollout-phone2optiplex.sh [dry|apply|verify]
#  default   : DRY RUN (add 'apply' to execute)
#  requires  : rsync + ssh on this host, rsync on $TARGET
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

TARGET="${TARGET:-optiplex}"
SRC_ROOT="/data/data/com.termux/files/home"
DST_ROOT="/home/jesse"
MODE="${1:-dry}"

mkdir -p "$HOME/tmp"
WORK="$(mktemp -d "$HOME/tmp/openroot-rollout.XXXXXXtrap 'rm -rf "$WORK"' EXIT

cat > "$WORK/files.txt" <<'OPENROOT_EOF'
bin/ledger-append
bin/say
bin/ask
bin/deepdive.py
bin/audit_repo.py
bin/aider-lite
bin/verify-chain
bin/fix-chain
bin/sol-anchor
bin/measure-drain
bin/acre-dashboard
bin/thermo-audit
bin/hive_entry.py
bin/relay_exec.sh
bin/cycle.sh
bin/sys_snapshot.sh
bin/wealth_log.sh
bin/ots_anchor.sh
bin/structure_enforcer.py
bin/immortal_context.py
bin/openroot-status
bin/aggressive_dedup.py
bin/backup_nontext_to_usb.sh
bin/move_home_sd_to_usb.sh
bin/clipboard_watcher.sh
bin/agape_fusion_loop.sh
bin/termics-compound-watch
bin/termics-bridge-any
bin/termics-mark-mistake
bin/termics-ledger
bin/termics-capture
bin/openroot
bin/openroot-inventory.py
bin/openroot-run
bin/openroot-absorb
bin/openroot-lattice
bin/openroot-keyword-scan
bin/thermo-snapshot
bin/bridge.py
bin/stctl
bin/rcstatus
bin/st-heal
bin/st-folder-opt
bin/une_master.py
bin/openroot-foundation-v3.sh
bin/or-status
bin/or-sync
bin/or-syncthing
bin/or-resume
bin/grand_unifying_script.sh
bin/or-oracle
bin/or-learn
bin/or-nodes
bin/optiplex
bin/or-coder
bin/stack_gate.sh
bin/a15_copy_symposium_from_download.sh
bin/find_green777.py
bin/a15_offload_v1.sh
bin/termux_clean_v1.sh
bin/openroot-diff
bin/openroot-safe-stage
bin/lumo_send.sh
bin/lumo_flush.sh
bin/file_access_hub_v2.sh
bin/lumo_clip.sh
bin/fetch2clip.sh
bin/ai-check
bin/a15-runner-v1
bin/a15_deepdive.sh
bin/a15_inventory.sh
bin/dedup_reclaim_v1.sh
bin/a15_inventory.sh.tmp
bin/dispatch_optiplex.sh
bin/beat.sh
bin/podpush.sh
bin/orphan_rescue_v1.sh
bin/orphan_transfer_v2.sh
bin/orphan_transfer_v3.sh
bin/promote_top10_orphans_v1.sh
bin/promote_top10_orphans_v2.sh
bin/pr_squash_survey_v1.sh
bin/pr121_squash_v1.sh
bin/secret_scrub_v1.sh
bin/openroot-ask.py
.local/bin/llama-server
.local/bin/llama-cli
.local/bin/rish
.local/bin/tlog
.local/bin/clip
.local/bin/distro
.local/bin/compost
.local/bin/bridge
.local/bin/openroot-query.bak.20261019T055235Z
.local/bin/openroot-query.bak.20261019T060846Z
.local/bin/<TOOL>
.local/bin/<TOOL>.bak.20261019T083044Z
openroot/bin/recall
openroot/bin/rescue_a15_unique.py
openroot/bin/relay_v1.py
openroot/bin/compound_v1.sh
openroot/bin/relay_v1.py.bak
openroot/bin/gh_audit_v2.sh
openroot/bin/mobile_audit_trigger.sh
openroot/bin/hygiene_fixes_v1.sh
openroot/bin/hygiene_fix_driver_v1.sh
openroot/bin/need_gate.py
openroot/bin/h003_log.py
openroot/bin/popw_hang.py
openroot/bin/triage100.py
openroot/bin/run_triage.py
openroot/bin/openroot_master_deploy.py
openroot/bin/sync_to_optiplex.sh
openroot/bin/abstract_grade.sh
openroot/bin/agape_node_bridge.sh
openroot/bin/agape_qa_engine.py
openroot/bin/asset_assign_pipeline.py
openroot/bin/asset_preclassify.py
openroot/bin/asset_preclassify_v2.py
openroot/bin/boardroom_router.py
openroot/bin/build_core_view.py
openroot/bin/core_view_server.sh
openroot/bin/cosmo_rack.py
openroot/bin/daily_loop_v1.sh
openroot/bin/db_recon.py
openroot/bin/db_tune.sh
openroot/bin/embed_index_v1.py
openroot/bin/fix_planetary_math_commit_v2.py
openroot/bin/fix_planetary_math_v1.py
openroot/bin/fleet_check_v1.sh
openroot/bin/fleet_closeout_v6_20260920.py
openroot/bin/fleet_snapshot_symposium.sh
openroot/bin/force_merge_push_v1.py
openroot/bin/frp10_probe.sh
openroot/bin/frp11_forensics.sh
openroot/bin/frp12_execute.sh
openroot/bin/frp5_deep_audit.sh
openroot/bin/frp6_fleet_squash.sh
openroot/bin/frp7_triage.sh
openroot/bin/frp8_prune_classify.sh
openroot/bin/frp9_tree_dedupe.sh
openroot/bin/gh_audit_v3.sh
openroot/bin/gh_audit_v3_patched.sh
openroot/bin/gh_hygiene_apply_v1.py
openroot/bin/git_push_delete_v9_20260920.py
openroot/bin/hygiene_fix_driver_v3.sh
openroot/bin/hype_gate.sh
openroot/bin/knowledge_probe_v1.py
openroot/bin/knowledge_weave.sh
openroot/bin/large_file_cleanup.py
openroot/bin/lb.sh
openroot/bin/lessons_v1.sh
openroot/bin/license_fleet_continue_v1.py
openroot/bin/llm_rag_integration.py
openroot/bin/lumo_lib.py
openroot/bin/master_finalize_v1.sh
openroot/bin/master_finalize_v2.sh
openroot/bin/master_finalize_v3.sh
openroot/bin/master_harvest_v3_20260920.py
openroot/bin/master_purge_v7_20260920.py
openroot/bin/master_salvage_v1.sh
openroot/bin/master_truth_v10_20260920.py
openroot/bin/merge_pr59_v1.sh
openroot/bin/merge_pr59_v2.sh
openroot/bin/merge_pr59_v3.sh
openroot/bin/mesh_fix_v3.sh
openroot/bin/mesh_publish_v2.sh
openroot/bin/mesh_recruit_v1.sh
openroot/bin/mesh_refine_v1.sh
openroot/bin/mesh_retry_v1.sh
openroot/bin/mesh_ship_v2.sh
openroot/bin/model_prune.sh
openroot/bin/model_symposium.py
openroot/bin/next_actions_20260920_v1.sh
openroot/bin/next_actions_v2_20260920.py
openroot/bin/ollama_diagnose.sh
openroot/bin/openroot_mcp_v1.py
openroot/bin/pr59_reopen_squash_v2.py
openroot/bin/pr_intake.sh
openroot/bin/profile_update_v1.sh
openroot/bin/queue_advance_v1.py
openroot/bin/queue_directive.py
openroot/bin/readme_contributors.sh
openroot/bin/recover_v1.sh
openroot/bin/0000_agape_one.py
openroot/bin/refinement_loop_v2.sh
openroot/bin/refinement_loop_v3.sh
openroot/bin/repo_clean_v1.sh
openroot/bin/research_ready_v1.sh
openroot/bin/resolve_pr58_final.py
openroot/bin/resolve_pr58_v1.sh
openroot/bin/restore_readme_profile_landing_v1.py
openroot/bin/run_handoff_v1.sh
openroot/bin/seal_session_v1.sh
openroot/bin/secure_and_commit_v4_20260920.py
openroot/bin/secure_and_commit_v5_20260920.py
openroot/bin/session_seal_v2.py
openroot/bin/sqlite_params.py
openroot/bin/task_recall.sh
openroot/bin/unified_workflow_v1.py
openroot/bin/universal_index_pipeline.py
openroot/bin/universal_unpack.py
openroot/bin/weekly_audit_v1.sh
openroot/bin/write_context_bridge.sh
openroot/bin/zd_census.py
openroot/bin/zombie_ref_kill_v8_20260920.py
openroot/bin/init_knowledge_db.py
openroot/bin/doc_compile.py
openroot/bin/agent.sh
openroot/bin/aider_task_runner.py
openroot/bin/env_map.py
openroot/bin/finalize_workflow.sh
openroot/bin/light_cone_router.py
openroot/bin/rebuild_core_workflow.sh
openroot/bin/0001_bridge.py
openroot/bin/0016_openroot.py
openroot/bin/refine_next.sh
openroot/bin/tier_dispatch_v1.py
openroot/bin/config_tiers.py
openroot/bin/contribution_tier_v1.py
openroot/bin/lb_stack_gate_all.sh
openroot/bin/multi_router.py
openroot/bin/hive_nursery.py
openroot/bin/window_extract_v1.py
openroot/bin/agape_cascade_v2.py
openroot/bin/agape_cascade_v21.py
openroot/bin/agape_cascade_v22.py
openroot/bin/agape_cascade_v23.py
openroot/bin/agape_cascade_v24.py
openroot/bin/fuse_router_lb_seal_v1.sh
openroot/bin/keyword_router_v1.py
openroot/bin/lesson_stage_v1.py
openroot/bin/lumo_bridge_bot_v1.py
openroot/bin/superlinear.sh
openroot/bin/window_cadence_v1.sh
openroot/bin/agape_cascade_v28.py
openroot/bin/cascade_release_v2.sh
openroot/bin/0003_agape_clean.py
openroot/bin/0004_une_client.py
openroot/bin/0006_agape_slim.py
openroot/bin/0008_raise_to_6n6.py
openroot/bin/0010_groq_fallback.py
openroot/bin/0012_newton_chain.py
openroot/bin/0013_local_rag_search.py
openroot/bin/0014_agape_hierarchical_raising.py
openroot/bin/0017_mdpipe.py
openroot/bin/0018_test_phone_tasks.py
openroot/bin/0019_enhance_tasks_with_efficiency.py
openroot/bin/0021_fs_hook_patch.py
openroot/bin/0022_agape_init.py
openroot/bin/0025_fix_chain_verify.py
openroot/bin/0026_openroot_hub.py
openroot/bin/0027_agape_frequency.py
openroot/bin/0028_agape_neurogenic_kernel.py
openroot/bin/0029_agape_evolution_v2.py
openroot/bin/0031_unified_agape_engine.py
openroot/bin/0034_repair_all_une_and_commit.py
openroot/bin/0037_fix_last_une_error.py
openroot/bin/0038_hive_swarm.py
openroot/bin/0043_master_codebase_orchestrator.py
openroot/bin/0044_v7.py
openroot/bin/0047_joule_leverage_analyzer.py
openroot/bin/0049_patch_voice.py
openroot/bin/0052_une_atomic_library.py
openroot/bin/0057_agape_primitive_forge.py
openroot/bin/0060_emergency_syntax_fix.py
openroot/bin/0061_diagnose_and_fix.py
openroot/bin/0062_diag_fix.py
openroot/bin/0064_fix_final.py
openroot/bin/0066_storage_daemon.py
openroot/bin/0067_fast_backup_daemon.py
openroot/bin/0068_agape_net_setup.py
openroot/bin/0069_agape_net_full_integration.py
openroot/bin/0070_index_content_blobs.py
openroot/bin/0071_une_fix.py
openroot/bin/0074_hive_entry.py
openroot/bin/0075_structure_enforcer.py
openroot/bin/0076_immortal_context.py
openroot/bin/0079_bridge.py
openroot/bin/0080_une_master.py
openroot/bin/0082_autoupdate_loop.py
openroot/bin/0083_cb_user_hunter.py
openroot/bin/0085_rmh.py
openroot/bin/0086_groq_max_cycles.py
openroot/bin/0090_une_atomic_library.py
openroot/bin/0091_justice_module.py
openroot/bin/0095_deploy_thermal_loop.py
openroot/bin/0100_find_dupes.py
openroot/bin/0101_setup.py
openroot/bin/0102_esp32_btbufs.py
openroot/bin/0104_organize_docs_a15.py
openroot/bin/0105_organize_docs_a15_v2.py
openroot/bin/0109_coordination.py
openroot/bin/0110_eta.py
openroot/bin/0111_next_joule.py
openroot/bin/0112_postulates.py
openroot/bin/0114_synergy.py
openroot/bin/0117_build_as_lib.py
openroot/bin/0119_merge-bin.py
openroot/bin/0120_test_thermo_optimizer.py
openroot/bin/0122_build_hex.py
openroot/bin/0125_base64_to_hex.py
openroot/bin/0133_generate_ci_matrix.py
openroot/bin/0135_genpartitions.py
openroot/bin/0136_platformio-custom.py
openroot/bin/0142_uf2conv.py
openroot/bin/0144_add_mbedtls_sources.py
openroot/bin/0145_lockdown_provision.py
openroot/bin/0149_core.py
openroot/bin/0150___init__.py
openroot/bin/0153___main__.py
openroot/bin/0154___pip-runner__.py
openroot/bin/0158_configuration.py
openroot/bin/0160_main.py
openroot/bin/0163_wheel_builder.py
openroot/bin/0164___init__.py
openroot/bin/0168_cache.py
openroot/bin/0170_filewrapper.py
openroot/bin/0172_serialize.py
openroot/bin/0173_wrapper.py
openroot/bin/0177___init__.py
openroot/bin/0178_compat.py
openroot/bin/0180_scripts.py
openroot/bin/0181_util.py
openroot/bin/0182___init__.py
openroot/bin/0183_codec.py
openroot/bin/0189_uts46data.py
openroot/bin/0191_exceptions.py
openroot/bin/0195__elffile.py
openroot/bin/0196__manylinux.py
openroot/bin/0198__parser.py
openroot/bin/0199__structures.py
openroot/bin/0201_dependency_groups.py
openroot/bin/team_gate_v2.sh
openroot/bin/terminal_log_rag.py
openroot/bin/bot_stop.sh
openroot/bin/markor_compiler.py
openroot/bin/compound_orchestrate.sh
openroot/bin/openrouter_client_v1.py
openroot/bin/contribution_tier_v2.py
openroot/bin/lb_loop_v2.py
openroot/bin/lb_stack_sweep.sh
openroot/bin/lb_team_gate_call.sh
openroot/bin/agape_cascade_v25.py
openroot/bin/agape_cascade_v27.py
openroot/bin/0002_groq_max_cycles.py
openroot/bin/lesson_ingest.py
openroot/bin/lumo_bridge_run.sh
openroot/bin/popw_ledger.py
openroot/bin/qa_fts5.py
openroot/bin/readme_draft_loop.sh
openroot/bin/window_fuse_v1.py
openroot/bin/agape_cascade_v26.py
openroot/bin/key_setup_fuse_v2.sh
openroot/bin/lb_commit_seal_v2.sh
openroot/bin/0005_test_une_full.py
openroot/bin/0007_faiss_search.py
openroot/bin/0009_batch_nomic_embed.py
openroot/bin/0011_one_principle_n_power_n.py
openroot/bin/route_yield.py
openroot/bin/0020_apply_fs_hook.py
openroot/bin/0023_constitutive_voice_engine.py
openroot/bin/0024_constitutive_compiler.py
openroot/bin/0033_repair_une_syntax.py
openroot/bin/0035_compressor_node.py
openroot/bin/0036_core_engine.py
openroot/bin/0039_apape_net_setup.py
openroot/bin/0040_map_files.py
openroot/bin/0041_inspect_map.py
openroot/bin/0042_build_coder_environment.py
openroot/bin/0045_swarm_bench.py
openroot/bin/0046_smoke_fix.py
openroot/bin/0048_snapshot_bootstrap.py
openroot/bin/0050_agape_farm_os.py
openroot/bin/0051_une_max_efficiency_lang.py
openroot/bin/0053_agape_kernel_v2.py
openroot/bin/0054_agape_ledger_chain.py
openroot/bin/0055_und_protocol.py
openroot/bin/0056_agape_node_bootstrap.py
openroot/bin/0058_run_7b_coder.py
openroot/bin/0059_final_une_syntax_pass.py
openroot/bin/0063_surgical_fix.py
openroot/bin/0065_agapenet_unified_setup.py
openroot/bin/0072_deepdive.py
openroot/bin/0073_audit_repo.py
openroot/bin/0077_aggressive_dedup.py
openroot/bin/0078_openroot-inventory.py
openroot/bin/0081_governor.py
openroot/bin/0097_search.py
openroot/bin/0084_dorks-eye.py
openroot/bin/0087_agape_synergetic_calculus.py
openroot/bin/0088_CREWAI_EXAMPLE.py
openroot/bin/0089_agapenet_cosmos_engine.py
openroot/bin/0092_laser_sim.py
openroot/bin/0093_deploy_openroot_kernel.py
openroot/bin/0094_deploy_v101.py
openroot/bin/0096_deploy_v103_evap.py
openroot/bin/0098_local_scan.py
openroot/bin/0099_scan_all.py
openroot/bin/0103_release_hashes.py
openroot/bin/0106_init.py
openroot/bin/0107_agape_mesh_oracle.py
openroot/bin/0108_sync_bridge.py
openroot/bin/0113_selftest.py
openroot/bin/0115_thermal_loop.py
openroot/bin/0116_git_rev_macro.py
openroot/bin/0118_create-uf2.py
openroot/bin/0121_uf2conv.py
openroot/bin/0123__rewrite_proto_namespace.py
openroot/bin/0124_analyze_map.py
openroot/bin/0126_build-userprefs-json.py
openroot/bin/0127_buildinfo.py
openroot/bin/0128_bump_version.py
openroot/bin/0129_collect_sizes.py
openroot/bin/0130_eth-ota-upload.py
openroot/bin/0131_exception_decoder.py
openroot/bin/0132_gen-fake-nodedb-seed.py
openroot/bin/0134_generate_release_notes.py
openroot/bin/0137_platformio-pre.py
openroot/bin/0138_readprops.py
openroot/bin/0139_seed-json-to-proto.py
openroot/bin/0140_size_report.py
openroot/bin/0141_test_size_scripts.py
openroot/bin/0143_filter_c3_exception_decoder.py
openroot/bin/0146___init__.py
openroot/bin/0147_core.py
openroot/bin/0148___init__.py
openroot/bin/0151_core.py
openroot/bin/0152___init__.py
openroot/bin/0155___init__.py
openroot/bin/0156_build_env.py
openroot/bin/0157_cache.py
openroot/bin/0159_exceptions.py
openroot/bin/0161_pyproject.py
openroot/bin/0162_self_outdated_check.py
openroot/bin/0165___init__.py
openroot/bin/0166__cmd.py
openroot/bin/0167_adapter.py
openroot/bin/0169_controller.py
openroot/bin/0171_heuristics.py
openroot/bin/0174___init__.py
openroot/bin/0175___main__.py
openroot/bin/0176_core.py
openroot/bin/0179_resources.py
openroot/bin/0184_compat.py
openroot/bin/0185_core.py
openroot/bin/0186_idnadata.py
openroot/bin/0187_intranges.py
openroot/bin/0188_package_data.py
openroot/bin/0190___init__.py
openroot/bin/0192_ext.py
openroot/bin/0193_fallback.py
openroot/bin/0194___init__.py
openroot/bin/0203_errors.py
openroot/bin/0208_specifiers.py
openroot/bin/0215_android.py
openroot/bin/0218_unix.py
openroot/bin/0222___main__.py
openroot/bin/0228_plugin.py
openroot/bin/0237__impl.py
openroot/bin/0239___version__.py
openroot/bin/0240__internal_utils.py
openroot/bin/0243_auth.py
openroot/bin/0248_help.py
openroot/bin/0249_hooks.py
openroot/bin/0251_packages.py
openroot/bin/0254_structures.py
openroot/bin/0255_utils.py
openroot/bin/0256___init__.py
openroot/bin/0260___init__.py
openroot/bin/0262__cell_widths.py
openroot/bin/0266__extension.py
openroot/bin/0267__fileno.py
openroot/bin/0268__inspect.py
openroot/bin/0269__log_render.py
openroot/bin/0270__loop.py
openroot/bin/0272__palettes.py
openroot/bin/0273__pick.py
openroot/bin/0282_abc.py
openroot/bin/0283_align.py
openroot/bin/0286_box.py
openroot/bin/0287_cells.py
openroot/bin/0289_color_triplet.py
openroot/bin/0291_console.py
openroot/bin/0294_control.py
openroot/bin/0299_file_proxy.py
openroot/bin/0302_json.py
openroot/bin/0304_layout.py
openroot/bin/0308_markup.py
openroot/bin/0311_pager.py
openroot/bin/0312_palette.py
openroot/bin/0313_panel.py
openroot/bin/0321_rule.py
openroot/bin/0326_status.py
openroot/bin/0330_table.py
openroot/bin/0333_theme.py
openroot/bin/0334_themes.py
openroot/bin/0335_traceback.py
openroot/bin/0346__openssl.py
openroot/bin/0352__request_methods.py
openroot/bin/0356_exceptions.py
openroot/bin/0359_poolmanager.py
openroot/bin/0360_response.py
openroot/bin/0369_request.py
openroot/bin/0370_response.py
openroot/bin/0373_ssl_match_hostname.py
openroot/bin/0374_ssltransport.py
openroot/bin/0379___init__.py
openroot/bin/0387_exceptions.py
openroot/bin/0389___init__.py
openroot/bin/0395__mapping.py
openroot/bin/0398__mapping.py
openroot/bin/0400__spdx.py
openroot/bin/0402_file_cache.py
openroot/bin/0405_autocompletion.py
openroot/bin/0409_index_command.py
openroot/bin/0414_req_command.py
openroot/bin/0415_spinners.py
openroot/bin/0416_status_codes.py
openroot/bin/0419_check.py
openroot/bin/0421_configuration.py
openroot/bin/0423_download.py
openroot/bin/0424_freeze.py
openroot/bin/0427_index.py
openroot/bin/0429_install.py
openroot/bin/0431_lock.py
openroot/bin/0432_search.py
openroot/bin/0435_wheel.py
openroot/bin/0436___init__.py
openroot/bin/0437_base.py
openroot/bin/0439_sdist.py
openroot/bin/0442_collector.py
openroot/bin/0443_package_finder.py
openroot/bin/0446__distutils.py
openroot/bin/0451_base.py
openroot/bin/0452_pkg_resources.py
openroot/bin/0453___init__.py
openroot/bin/0455_direct_url.py
openroot/bin/0461_scheme.py
openroot/bin/0462_search_scope.py
openroot/bin/0467_auth.py
openroot/bin/0469_download.py
openroot/bin/0470_lazy_wheel.py
openroot/bin/0485_base.py
openroot/bin/0486__jaraco_text.py
openroot/bin/0490_compatibility_tags.py
openroot/bin/0491_datetime.py
openroot/bin/0492_deprecation.py
openroot/bin/0495_entrypoints.py
openroot/bin/0500_logging.py
openroot/bin/0503_pylock.py
openroot/bin/0504_retry.py
openroot/bin/0509_virtualenv.py
openroot/bin/0511___init__.py
openroot/bin/0525_resolver.py
openroot/bin/0530__dists.py
openroot/bin/0531__envs.py
openroot/bin/0533_chunk_and_seed.py
openroot/bin/0536_bench.py
openroot/bin/0542_fuzz.py
openroot/bin/0543_generate_legacy_db.py
openroot/bin/0544_helpers.py
openroot/bin/0546_test-auxiliary.py
openroot/bin/0553_test-ivf-rename.py
openroot/bin/0558_test-metadata.py
openroot/bin/0561_test-rescore-mutations.py
openroot/bin/0566_test-correctness.py
openroot/bin/0574_bench_delete.py
openroot/bin/0575_test_smoke.py
openroot/bin/0577_build_base_db.py
openroot/bin/0579_build-contents.py
openroot/bin/0583_fit_plot.py
openroot/bin/0586_axiom_cli.py
openroot/bin/0587_merge_kb.py
openroot/bin/0591_rmh_labyrinth_model.py
openroot/bin/0592_psychrometric_model.py
openroot/bin/0595_nomen_core.py
openroot/bin/0597_canon.py
openroot/bin/0602_fusion_sensor_wrapper.py
openroot/bin/0605_synergetics_engine.py
openroot/bin/0606_build.py
openroot/bin/0624_openroot_classifier_loader.py
openroot/bin/0627_fusion_core.py
openroot/bin/0630_kai_query.py
openroot/bin/0634_platformio-clusterfuzzlite-post.py
openroot/bin/0635_platformio-clusterfuzzlite-pre.py
openroot/bin/0642_nrf52_warm_region.py
openroot/bin/0650_test_memleaks.py
openroot/bin/0651_test_posix.py
openroot/bin/0655_git_pre_commit.py
openroot/bin/0657_print_api_speed.py
openroot/bin/0662_procinfo.py
openroot/bin/0664_winservices.py
openroot/bin/0665_chunk_sender.py
openroot/bin/0671_build_spec_v1.py
openroot/bin/0675_makefile_gen.py
openroot/bin/0682__compat.py
openroot/bin/0684__pslinux.py
openroot/bin/0746__psaix.py
openroot/bin/0211_version.py
openroot/bin/0223_console.py
openroot/bin/0225_formatter.py
openroot/bin/0226_lexer.py
openroot/bin/0231_sphinxext.py
openroot/bin/0233_token.py
openroot/bin/0234_unistring.py
openroot/bin/0235_util.py
openroot/bin/0244_certs.py
openroot/bin/0257_providers.py
openroot/bin/0258_reporters.py
openroot/bin/0276__stack.py
openroot/bin/0278__win32_console.py
openroot/bin/0281__wrap.py
openroot/bin/0285_bar.py
openroot/bin/0293_containers.py
openroot/bin/0295_default_styles.py
openroot/bin/0329_syntax.py
openroot/bin/0338__parser.py
openroot/bin/0340__types.py
openroot/bin/0341___init__.py
openroot/bin/0348__windows.py
openroot/bin/0349___init__.py
openroot/bin/0350__base_connection.py
openroot/bin/0353__version.py
openroot/bin/0358_filepost.py
openroot/bin/0364_connection.py
openroot/bin/0365_probe.py
openroot/bin/0366___init__.py
openroot/bin/0371_retry.py
openroot/bin/0378_wait.py
openroot/bin/0382_request.py
openroot/bin/0386_criterion.py
openroot/bin/0388_resolution.py
openroot/bin/0394___init__.py
openroot/bin/0396_python.py
openroot/bin/0403_redis_cache.py
openroot/bin/0408_command_context.py
openroot/bin/0412_parser.py
openroot/bin/0413_progress_bars.py
openroot/bin/0417___init__.py
openroot/bin/0433_show.py
openroot/bin/0438_installed.py
openroot/bin/0441___init__.py
openroot/bin/0447__sysconfig.py
openroot/bin/0450__json.py
openroot/bin/0454_candidate.py
openroot/bin/0456_format_control.py
openroot/bin/0465_wheel.py
openroot/bin/0466___init__.py
openroot/bin/0471_session.py
openroot/bin/0472_utils.py
openroot/bin/0474_check.py
openroot/bin/0477___init__.py
openroot/bin/0484_req_uninstall.py
openroot/bin/0493_direct_url_helpers.py
openroot/bin/0496_filesystem.py
openroot/bin/0498_glibc.py
openroot/bin/0499_hashes.py
openroot/bin/0501_misc.py
openroot/bin/0502_packaging.py
openroot/bin/0513_git.py
openroot/bin/0516_versioncontrol.py
openroot/bin/0517_resolver.py
openroot/bin/0519_candidates.py
openroot/bin/0520_factory.py
openroot/bin/0527_wheel.py
openroot/bin/0532_joule_probe.py
openroot/bin/0538_ground_truth.py
openroot/bin/0547_test-cache-finalize.py
openroot/bin/0548_test-diskann.py
openroot/bin/0549_test-general.py
openroot/bin/0556_test-legacy-compat.py
openroot/bin/0557_test-loadable.py
openroot/bin/0563_utils.py
openroot/bin/0560_test-rename.py
openroot/bin/0568_demo.py
openroot/bin/0578_build-base.py
openroot/bin/0584_chord_lengths.py
openroot/bin/0585_pr-preflight.py
openroot/bin/0589_test_rmh_labyrinth_model.py
openroot/bin/0590_test_psychrometric_model.py
openroot/bin/0601_laser_sim.py
openroot/bin/0614_LXMPeer.py
openroot/bin/0619__version.py
openroot/bin/0621_example_sender.py
openroot/bin/0623_openroot-classifier.py
openroot/bin/0629_embed_kai.py
openroot/bin/0636_router_fuzzer_seed_corpus.py
openroot/bin/0638_esp32_extra.py
openroot/bin/0639_esp32_pre.py
openroot/bin/0641_nrf52_extra.py
openroot/bin/0643_nrf54l15_linker.py
openroot/bin/0645_windows_link_flags.py
openroot/bin/0647__pssunos.py
openroot/bin/0648_test_connections.py
openroot/bin/0653_bench_oneshot.py
openroot/bin/0654_generate_manifest.py
openroot/bin/0658_iotop.py
openroot/bin/0659_netstat.py
openroot/bin/0660_pidof.py
openroot/bin/0661_pmap.py
openroot/bin/0668_generate_grant_doc.py
openroot/bin/0672_desiccant_module_v1.py
openroot/bin/0680_mqtt_basic.py
openroot/bin/0687___main__.py
openroot/bin/0689_test_process.py
openroot/bin/0690_test_system.py
openroot/bin/0691_test_testutils.py
openroot/bin/0698_print_hashes.py
openroot/bin/0700_pstree.py
openroot/bin/0704_breath_loop_v6_radiative.py
openroot/bin/0710_settings.py
openroot/bin/0712_test_une_fixed.py
openroot/bin/0714_test_contracts.py
openroot/bin/0715_test_misc.py
openroot/bin/0719_bench_oneshot_2.py
openroot/bin/0725_print_announce.py
openroot/bin/0729_procsmem.py
openroot/bin/0730_sensors.py
openroot/bin/0737_custom_build_tasks.py
openroot/bin/0742_test_une_now.py
openroot/bin/0748_test_aix.py
openroot/bin/0752_print_timeline.py
openroot/bin/0754_top.py
openroot/bin/0756_thesis_chunker.py
openroot/bin/0757_diagnostic.py
openroot/bin/0759_server.py
openroot/bin/0767_test_thermo.py
openroot/bin/0772_import_unified.py
openroot/bin/0774_reorganize_postulates.py
openroot/bin/0778_theorem_generator.py
openroot/bin/0779_theorem_generator_batch2.py
openroot/bin/0780_theorem_generator_batch3.py
openroot/bin/0785_or_coder_node.py
openroot/bin/0799___init__.py
openroot/bin/0803_Channel.py
openroot/bin/0202_direct_url.py
openroot/bin/0204_markers.py
openroot/bin/0206_pylock.py
openroot/bin/0209_tags.py
openroot/bin/0219_version.py
openroot/bin/0221___init__.py
openroot/bin/0227_modeline.py
openroot/bin/0230_scanner.py
openroot/bin/0232_style.py
openroot/bin/0242_api.py
openroot/bin/0246_cookies.py
openroot/bin/0250_models.py
openroot/bin/0253_status_codes.py
openroot/bin/0259_structs.py
openroot/bin/0261___main__.py
openroot/bin/0264__emoji_replace.py
openroot/bin/0265__export_format.py
openroot/bin/0271__null_file.py
openroot/bin/0274__ratio.py
openroot/bin/0279__windows.py
openroot/bin/0280__windows_renderer.py
openroot/bin/0292_constrain.py
openroot/bin/0297_emoji.py
openroot/bin/0301_highlighter.py
openroot/bin/0305_live.py
openroot/bin/0307_logging.py
openroot/bin/0309_measure.py
openroot/bin/0314_pretty.py
openroot/bin/0315_progress.py
openroot/bin/0316_progress_bar.py
openroot/bin/0319_region.py
openroot/bin/0322_scope.py
openroot/bin/0323_screen.py
openroot/bin/0324_segment.py
openroot/bin/0325_spinner.py
openroot/bin/0327_style.py
openroot/bin/0336_tree.py
openroot/bin/0337___init__.py
openroot/bin/0343___init__.py
openroot/bin/0347__ssl_constants.py
openroot/bin/0354_connection.py
openroot/bin/0355_connectionpool.py
openroot/bin/0361_pyopenssl.py
openroot/bin/0363___init__.py
openroot/bin/0367_connection.py
openroot/bin/0375_timeout.py
openroot/bin/0380_connection.py
openroot/bin/0381_fetch.py
openroot/bin/0383_response.py
openroot/bin/0384___init__.py
openroot/bin/0390__in_process.py
openroot/bin/0391___init__.py
openroot/bin/0393__mapping.py
openroot/bin/0397___init__.py
openroot/bin/0401___init__.py
openroot/bin/0404___init__.py
openroot/bin/0406_base_command.py
openroot/bin/0407_cmdoptions.py
openroot/bin/0418_cache.py
openroot/bin/0420_completion.py
openroot/bin/0425_hash.py
openroot/bin/0430_list.py
openroot/bin/0434_uninstall.py
openroot/bin/0440_wheel.py
openroot/bin/0449___init__.py
openroot/bin/0457_index.py
openroot/bin/0459_link.py
openroot/bin/0464_target_python.py
openroot/bin/0468_cache.py
openroot/bin/0475_freeze.py
openroot/bin/0479_pep723.py
openroot/bin/0480_req_dependency_group.py
openroot/bin/0494_egg_link.py
openroot/bin/0505_subprocess.py
openroot/bin/0508_urls.py
openroot/bin/0512_bazaar.py
openroot/bin/0518_base.py
openroot/bin/0522_provider.py
openroot/bin/0537_faiss_kmeans.py
openroot/bin/0539_profile.py
openroot/bin/0540_amalgamate.py
openroot/bin/0541_conftest.py
openroot/bin/0550_test-insert-delete.py
openroot/bin/0554_test-ivf.py
openroot/bin/0564_test-afbd.py
openroot/bin/0567_openai-sample.py
openroot/bin/0572_knn.py
openroot/bin/0580_distill-model.py
openroot/bin/0581_build-base.py
openroot/bin/0588_canon.py
openroot/bin/0593_generate_rmh_report.py
openroot/bin/0594_nomen.py
openroot/bin/0596_thermo_ledger.py
openroot/bin/0599_gh_termux_python_primer.py
openroot/bin/0600_justice_module.py
openroot/bin/0603_extract_seed.py
openroot/bin/0609_esptool.py
openroot/bin/0612_Handlers.py
openroot/bin/0616_LXMessage.py
openroot/bin/0617_LXStamper.py
openroot/bin/0620_example_receiver.py
openroot/bin/0633_fix_bsec_lib.py
openroot/bin/0656_print_access_denied.py
openroot/bin/0663_ps.py
openroot/bin/0666_thesis_hash.py
openroot/bin/0667_collector.py
openroot/bin/0669_make_final_grant.py
openroot/bin/0673_gen_whitepaper.py
openroot/bin/0676_phi_spiral_v9.py
openroot/bin/0677_physics_ledger_v1.py
openroot/bin/0678_physics_ledger_v2.py
openroot/bin/0686__psposix.py
openroot/bin/0688_test_osx.py
openroot/bin/0693_disk_usage.py
openroot/bin/0694_free.py
openroot/bin/0695_ifconfig.py
openroot/bin/0696_print_dist.py
openroot/bin/0697_print_downloads.py
openroot/bin/0699_winmake.py
openroot/bin/0703_LearnFromMistakes.py
openroot/bin/0705_earth_loop_v8.py
openroot/bin/0706_organize.py
openroot/bin/0707_recruitment_portal.py
openroot/bin/0708_thermal_battery_system.py
openroot/bin/0720_check_broken_links.py
openroot/bin/0722_convert_readme.py
openroot/bin/0723_download_wheels_appveyor.py
openroot/bin/0727_meminfo.py
openroot/bin/0728_nettop.py
openroot/bin/0731_create_session_anchor.py
openroot/bin/0732_generate_grant_summary.py
openroot/bin/0734_bump_metainfo.py
openroot/bin/0738_mqtt_publish_in_callback.py
openroot/bin/0743_test_with_server.py
openroot/bin/0749_test_bsd.py
openroot/bin/0751_test_sunos.py
openroot/bin/0758_fix_errors.py
openroot/bin/0761_deploy_v101.py
openroot/bin/0766_axiom_mesh_sync_optiplex.py
openroot/bin/0769_derive_constants.py
openroot/bin/0777_seven_symbols_recovery.py
openroot/bin/0786_test_tidbit_library.py
openroot/bin/0787_generate_rmh_report.py
openroot/bin/0789_selftest.py
openroot/bin/0197__musllinux.py
openroot/bin/0200__tokenizer.py
openroot/bin/0205_metadata.py
openroot/bin/0207_requirements.py
openroot/bin/0210_utils.py
openroot/bin/0212___init__.py
openroot/bin/0213___init__.py
openroot/bin/0214___main__.py
openroot/bin/0216_api.py
openroot/bin/0217_macos.py
openroot/bin/0220_windows.py
openroot/bin/0224_filter.py
openroot/bin/0229_regexopt.py
openroot/bin/0236___init__.py
openroot/bin/0238___init__.py
openroot/bin/0241_adapters.py
openroot/bin/0245_compat.py
openroot/bin/0247_exceptions.py
openroot/bin/0252_sessions.py
openroot/bin/0263__emoji_codes.py
openroot/bin/0275__spinners.py
openroot/bin/0277__timer.py
openroot/bin/0284_ansi.py
openroot/bin/0288_color.py
openroot/bin/0290_columns.py
openroot/bin/0296_diagnose.py
openroot/bin/0298_errors.py
openroot/bin/0300_filesize.py
openroot/bin/0303_jupyter.py
openroot/bin/0306_live_render.py
openroot/bin/0310_padding.py
openroot/bin/0317_prompt.py
openroot/bin/0318_protocol.py
openroot/bin/0320_repr.py
openroot/bin/0328_styled.py
openroot/bin/0331_terminal_theme.py
openroot/bin/0332_text.py
openroot/bin/0339__re.py
openroot/bin/0342__writer.py
openroot/bin/0344__api.py
openroot/bin/0345__macos.py
openroot/bin/0351__collections.py
openroot/bin/0357_fields.py
openroot/bin/0362_socks.py
openroot/bin/0368_proxy.py
openroot/bin/0372_ssl_.py
openroot/bin/0376_url.py
openroot/bin/0377_util.py
openroot/bin/0385_abstract.py
openroot/bin/0392___init__.py
openroot/bin/0399___init__.py
openroot/bin/0410_main.py
openroot/bin/0411_main_parser.py
openroot/bin/0422_debug.py
openroot/bin/0426_help.py
openroot/bin/0428_inspect.py
openroot/bin/0444_sources.py
openroot/bin/0445___init__.py
openroot/bin/0448_base.py
openroot/bin/0458_installation_report.py
openroot/bin/0460_release_control.py
openroot/bin/0463_selection_prefs.py
openroot/bin/0473_xmlrpc.py
openroot/bin/0476_prepare.py
openroot/bin/0478_constructors.py
openroot/bin/0481_req_file.py
openroot/bin/0482_req_install.py
openroot/bin/0483_req_set.py
openroot/bin/0487__log.py
openroot/bin/0488_appdirs.py
openroot/bin/0489_compat.py
openroot/bin/0497_filetypes.py
openroot/bin/0506_temp_dir.py
openroot/bin/0507_unpacking.py
openroot/bin/0510_wheel.py
openroot/bin/0514_mercurial.py
openroot/bin/0515_subversion.py
openroot/bin/0521_found_candidates.py
openroot/bin/0523_reporter.py
openroot/bin/0524_requirements.py
openroot/bin/0526___init__.py
openroot/bin/0528___init__.py
openroot/bin/0529__compat.py
openroot/bin/0534_feed_oracle.py
openroot/bin/0565_build.py
openroot/bin/0535_generate_system_map.py
openroot/bin/0545_skip.test-correctness.py
openroot/bin/0551_test-ivf-mutations.py
openroot/bin/0552_test-ivf-quantization.py
openroot/bin/0555_test-knn-distance-constraints.py
openroot/bin/0559_test-partition-keys.py
openroot/bin/0562_test-rescore.py
openroot/bin/0569_extra_init.py
openroot/bin/0570_bench.py
openroot/bin/0571_build.py
openroot/bin/0573_test.py
openroot/bin/0576_build_base_db.py
openroot/bin/0582_build-contents.py
openroot/bin/0598_generate_rmh_report.py
openroot/bin/0604_fusion_core.py
openroot/bin/0607_Example.py
openroot/bin/0608_RNode.py
openroot/bin/0610_gen_esp32part.py
openroot/bin/0611_spiffsgen.py
openroot/bin/0613_LXMF.py
openroot/bin/0615_LXMRouter.py
openroot/bin/0618___init__.py
openroot/bin/0622_lxmd.py
openroot/bin/0625_test_classifier.py
openroot/bin/0626_kernel_translator.py
openroot/bin/0628_fractak_swarm_engine.py
openroot/bin/0631_setup.py
openroot/bin/0632_conf.py
openroot/bin/0637_disable_adafruit_usb.py
openroot/bin/0640_ld_response_file.py
openroot/bin/0644_wasm_link_flags.py
openroot/bin/0646_testsuite.py
openroot/bin/0649_test_linux.py
openroot/bin/0652_test_windows.py
openroot/bin/0670_aerocement_triad_v1.py
openroot/bin/0674_generate_thesis.py
openroot/bin/0679_thermal_battery_check.py
openroot/bin/0681_test_full_integration.py
openroot/bin/0683__psbsd.py
openroot/bin/0685__psosx.py
openroot/bin/0692_test_unicode.py
openroot/bin/0702_who.py
openroot/bin/0711_test_acre_workflow.py
openroot/bin/0713__pswindows.py
openroot/bin/0716_battery.py
openroot/bin/0717_cpu_distribution.py
openroot/bin/0718_fans.py
openroot/bin/0721_clinter.py
openroot/bin/0733_unified_breath_loop_v3.py
openroot/bin/0736_stm32_extra.py
openroot/bin/0741_test_interactive.py
openroot/bin/0744_verify_system.py
openroot/bin/0745__common.py
openroot/bin/0747_runner.py
openroot/bin/0750_test_process_all.py
openroot/bin/0753_killall.py
openroot/bin/0765_rmh_labyrinth_model.py
openroot/bin/0768_agape_cooperation_theorem.py
openroot/bin/0775_sacred_language_theorem.py
openroot/bin/0781_theorem_generator_batch4.py
openroot/bin/0790___init__.py
openroot/bin/0791_solar.py
openroot/bin/0796_agape_board_advisor.py
openroot/bin/0701_temperatures.py
openroot/bin/0709_data_logger_example.py
openroot/bin/0724_download_wheels_github.py
openroot/bin/0739_quick_test.py
openroot/bin/0740_test_comprehensive.py
openroot/bin/0760_ai_bridge.py
openroot/bin/0762_generate_rmh_report.py
openroot/bin/0770_energy_theorems.py
openroot/bin/0773_proof_builder.py
openroot/bin/0776_sacred_merkle_system.py
openroot/bin/0793_setup.py
openroot/bin/0809_Minimal.py
openroot/bin/0817_Packet.py
openroot/bin/0818_Resolver.py
openroot/bin/0831_AES.py
openroot/bin/0836_PKCS7.py
openroot/bin/0857_WeaveInterface.py
openroot/bin/0858___init__.py
openroot/bin/0862_rnir.py
openroot/bin/0869_rnx.py
openroot/bin/0886_highlight.py
openroot/bin/0898_loop.py
openroot/bin/0901_retry.py
openroot/bin/0907___init__.py
openroot/bin/0908_netinfo.py
openroot/bin/0935_libc-util.py
openroot/bin/0936_unicode.py
openroot/bin/0949_ggml_to_pt.py
openroot/bin/0955_basic.py
openroot/bin/0969__connection.py
openroot/bin/0990___init__.py
openroot/bin/0994___init__.py
openroot/bin/1011_config.py
openroot/bin/1047__exceptions.py
openroot/bin/1048__main.py
openroot/bin/1063__models.py
openroot/bin/1068__types.py
openroot/bin/1074__logs.py
openroot/bin/1093_batch_list_response.py
openroot/bin/1119_chat_completion_content_part_text_param.py
openroot/bin/1136_error_object.py
openroot/bin/1145_transcriptions.py
openroot/bin/1152_base.py
openroot/bin/1153_default.py
openroot/bin/1155_wsgi.py
openroot/bin/1156__config.py
openroot/bin/1162__discriminated_union.py
openroot/bin/1190_tools.py
openroot/bin/1201_class_validators.py
openroot/bin/1202_color.py
openroot/bin/1213_main.py
openroot/bin/1229_http_proxy.py
openroot/bin/1242_http2.py
openroot/bin/1244_interfaces.py
openroot/bin/1253__resources.py
openroot/bin/1258__synchronization.py
openroot/bin/1272_file.py
openroot/bin/1285__psbsd.py
openroot/bin/1288__psposix.py
openroot/bin/1291_battery.py
openroot/bin/1297_iotop.py
openroot/bin/1301_nettop.py
openroot/bin/1306_ps.py
openroot/bin/1307_pstree.py
openroot/bin/1317_convert_readme.py
openroot/bin/1325_print_dist.py
openroot/bin/1336_test_connections.py
openroot/bin/1338_test_linux.py
openroot/bin/recovery_final_status.sh
openroot/bin/cicd_quarantine_seal_v1.sh
openroot/bin/0824_clean_md.py
openroot/bin/0828_identity.py
openroot/bin/0843___init__.py
openroot/bin/0856_UDPInterface.py
openroot/bin/0866_rnprobe.py
openroot/bin/0878_exceptions.py
openroot/bin/0879_log.py
openroot/bin/0883___init__.py
openroot/bin/0894_exception.py
openroot/bin/0899_process.py
openroot/bin/0903_session.py
openroot/bin/0905_RNodeInterface.py
openroot/bin/0919_bridge.py
openroot/bin/0922_glossary_linker.py
openroot/bin/0924_runner.py
openroot/bin/0926_unicode.py
openroot/bin/0928_gperf_fold_key_conv.py
openroot/bin/0931_make_unicode_fold_data.py
openroot/bin/0934_unicode.py
openroot/bin/0938_walk.py
openroot/bin/0939_create_text_files.py
openroot/bin/0943_convert-parakeet-to-ggml.py
openroot/bin/0964___init__.py
openroot/bin/0971__headers.py
openroot/bin/0985_lowlevel.py
openroot/bin/0986_pytest_plugin.py
openroot/bin/0997__api.py
openroot/bin/1002__trace.py
openroot/bin/1009_class_validators.py
openroot/bin/1018_fields.py
openroot/bin/1023_json_schema.py
openroot/bin/1027_parse.py
openroot/bin/1029_schema.py
openroot/bin/1032_types.py
openroot/bin/1037_version.py
openroot/bin/1044__config.py
openroot/bin/1050__multipart.py
openroot/bin/1051__status_codes.py
openroot/bin/1082__typing.py
openroot/bin/1084___init__.py
openroot/bin/1086_embeddings.py
openroot/bin/1099_file_create_params.py
openroot/bin/1103_file_list_response.py
openroot/bin/1111_translation.py
openroot/bin/1126_chat_completion_named_tool_choice_param.py
openroot/bin/1128_chat_completion_system_message_param.py
openroot/bin/1149_completions.py
openroot/bin/1157__core_metadata.py
openroot/bin/1178__serializers.py
openroot/bin/1184_class_validators.py
openroot/bin/1198___init__.py
openroot/bin/1200_annotated_types.py
openroot/bin/1206_decorator.py
openroot/bin/1212_json.py
openroot/bin/1215_networks.py
openroot/bin/1231_socks_proxy.py
openroot/bin/1234_base.py
openroot/bin/1252__fileio.py
openroot/bin/1254__signals.py
openroot/bin/1255__sockets.py
openroot/bin/1305_procsmem.py
openroot/bin/1310_top.py
openroot/bin/1328_print_timeline.py
openroot/bin/1332___main__.py
openroot/bin/1345_test_system.py
openroot/bin/1346_test_testutils.py
openroot/bin/agape_ledger_chain.py
openroot/bin/enable_vector_embeddings.py
openroot/bin/rollout_openroot.sh
openroot/bin/hive.sh
openroot/bin/thermal_frontier_v2_water.py
openroot/bin/0804_Echo.py
openroot/bin/0813_Speedtest.py
openroot/bin/0815_Channel.py
openroot/bin/0823__version.py
openroot/bin/0850_LocalInterface.py
openroot/bin/0854_SerialInterface.py
openroot/bin/0873_umsgpack.py
openroot/bin/0885_commitsigs.py
openroot/bin/0888_pages.py
openroot/bin/0889_server.py
openroot/bin/0910_aes128.py
openroot/bin/0914_ed25519_oop.py
openroot/bin/0917_emergency_rescue.py
openroot/bin/0921_script.py
openroot/bin/0927_dict_conv.py
openroot/bin/0954___init__.py
openroot/bin/0958_test_whisper_processor.py
openroot/bin/0959_whisper_processor.py
openroot/bin/0975__util.py
openroot/bin/0988_to_process.py
openroot/bin/1008_annotated_handlers.py
openroot/bin/1025_mypy.py
openroot/bin/1038_warnings.py
openroot/bin/1049__models.py
openroot/bin/1066__response.py
openroot/bin/1067__streaming.py
openroot/bin/1080__sync.py
openroot/bin/1087_files.py
openroot/bin/1089___init__.py
openroot/bin/1095_completion_usage.py
openroot/bin/1104_model.py
openroot/bin/1105_model_deleted.py
openroot/bin/1106_model_list_response.py
openroot/bin/1113___init__.py
openroot/bin/1114_chat_completion.py
openroot/bin/1118_chat_completion_content_part_param.py
openroot/bin/1132_chat_completion_tool_param.py
openroot/bin/1134_completion_create_params.py
openroot/bin/1137_function_definition.py
openroot/bin/1139___init__.py
openroot/bin/1159__dataclasses.py
openroot/bin/1161__decorators_v1.py
openroot/bin/1170__internal_dataclass.py
openroot/bin/1176__schema_gather.py
openroot/bin/1180__typing_extra.py
openroot/bin/1191___init__.py
openroot/bin/1193_missing_sentinel.py
openroot/bin/1203_config.py
openroot/bin/1210_fields.py
openroot/bin/1220_typing.py
openroot/bin/1238___init__.py
openroot/bin/1241_http11.py
openroot/bin/1243_http_proxy.py
openroot/bin/1247__trio.py
openroot/bin/1261__testing.py
openroot/bin/1268__subprocesses.py
openroot/bin/1273_memory.py
openroot/bin/1275_text.py
openroot/bin/1281___init__.py
openroot/bin/1284__psaix.py
openroot/bin/1286__pslinux.py
openroot/bin/1287__psosx.py
openroot/bin/1292_cpu_distribution.py
openroot/bin/1296_ifconfig.py
openroot/bin/1312_winservices.py
openroot/bin/1316_clinter.py
openroot/bin/1324_print_api_speed.py
openroot/bin/1326_print_downloads.py
openroot/bin/batch_nomic_embed.py
openroot/bin/cycle_manager.py
openroot/bin/final_cleanup.sh
openroot/bin/openroot_public_readiness.py
openroot/bin/aerocement_compile_review.py
openroot/bin/0802_Buffer.py
openroot/bin/0810_Ratchets.py
openroot/bin/0820_Reticulum.py
openroot/bin/0826_channel.py
openroot/bin/0827_hashes.py
openroot/bin/0830_conf.py
openroot/bin/0841_Token.py
openroot/bin/0848_Interface.py
openroot/bin/0852_RNodeInterface.py
openroot/bin/0853_RNodeMultiInterface.py
openroot/bin/0864_rnpath.py
openroot/bin/0877_aiosam.py
openroot/bin/0897_listener.py
openroot/bin/0915_eddsa.py
openroot/bin/0923_pyo3_version.py
openroot/bin/0929_gperf_unfold_key_conv.py
openroot/bin/0953_eval.py
openroot/bin/0960_eleven-labs.py
openroot/bin/0963_typing_extensions.py
openroot/bin/0966__version.py
openroot/bin/0973__receivebuffer.py
openroot/bin/0976__version.py
openroot/bin/0992_introspection.py
openroot/bin/0995_core_schema.py
openroot/bin/0999__models.py
openroot/bin/1001__synchronization.py
openroot/bin/1005__migration.py
openroot/bin/1007_aliases.py
openroot/bin/1012_dataclasses.py
openroot/bin/1015_env_settings.py
openroot/bin/1017_errors.py
openroot/bin/1046__decoders.py
openroot/bin/1055__utils.py
openroot/bin/1058__client.py
openroot/bin/1059__compat.py
openroot/bin/1081__transform.py
openroot/bin/1091_batch_create_params.py
openroot/bin/1098_embedding_create_params.py
openroot/bin/1109_transcription.py
openroot/bin/1112_translation_create_params.py
openroot/bin/1116_chat_completion_chunk.py
openroot/bin/1124_chat_completion_message_tool_call.py
openroot/bin/1140_function_definition.py
openroot/bin/1144_speech.py
openroot/bin/1168__git.py
openroot/bin/1173__model_construction.py
openroot/bin/1175__repr.py
openroot/bin/1177__schema_generation_shared.py
openroot/bin/1183__validators.py
openroot/bin/1186_copy_internals.py
openroot/bin/1196__loader.py
openroot/bin/1209_errors.py
openroot/bin/1211_generics.py
openroot/bin/1224___init__.py
openroot/bin/1235_mock.py
openroot/bin/1239_connection.py
openroot/bin/1240_connection_pool.py
openroot/bin/1249__contextmanagers.py
openroot/bin/1267__streams.py
openroot/bin/1274_stapled.py
openroot/bin/1277_test_sniffio.py
openroot/bin/1279_setup.py
openroot/bin/1289__pssunos.py
openroot/bin/1298_killall.py
openroot/bin/1304_procinfo.py
openroot/bin/1314_bench_oneshot_2.py
openroot/bin/1323_print_announce.py
openroot/bin/1330_winmake.py
openroot/bin/1331___init__.py
openroot/bin/1347_test_unicode.py
openroot/bin/thermal_frontier_v1.py
openroot/bin/0726_purge_installation.py
openroot/bin/0735_nrf52_lto.py
openroot/bin/0755_emergency_rescue.py
openroot/bin/0763_logger.py
openroot/bin/0764_psychrometric_model.py
openroot/bin/0771_import_euclid.py
openroot/bin/0782_theorem_generator_batch5.py
openroot/bin/0783_theorems_extend.py
openroot/bin/0784_or_coder.py
openroot/bin/0788___init__.py
openroot/bin/0792_rmh_lab.py
openroot/bin/0808_Link.py
openroot/bin/0821_Transport.py
openroot/bin/0825_all.py
openroot/bin/0832_Ed25519.py
openroot/bin/0840_SHA512.py
openroot/bin/0851_PipeInterface.py
openroot/bin/0860_rncp.py
openroot/bin/0881_tunnel.py
openroot/bin/0884_client.py
openroot/bin/0891___init__.py
openroot/bin/0892__version.py
openroot/bin/0893_args.py
openroot/bin/0900_protocol.py
openroot/bin/0909___init__.py
openroot/bin/0916_emergency_rescue.py
openroot/bin/0918_compost.py
openroot/bin/0925___init__.py
openroot/bin/0930_make_unicode_egcb_data.py
openroot/bin/0942_convert-h5-to-ggml.py
openroot/bin/0950_bench.py
openroot/bin/0957_generate_cu_files.py
openroot/bin/0962___init__.py
openroot/bin/0972__readers.py
openroot/bin/0977__writers.py
openroot/bin/0979___main__.py
openroot/bin/0982_from_thread.py
openroot/bin/1000__ssl.py
openroot/bin/1003__utils.py
openroot/bin/1014_decorator.py
openroot/bin/1024_main.py
openroot/bin/1026_networks.py
openroot/bin/1028_root_model.py
openroot/bin/1036_validators.py
openroot/bin/1039___init__.py
openroot/bin/1045__content.py
openroot/bin/1061__exceptions.py
openroot/bin/1069__version.py
openroot/bin/1070___init__.py
openroot/bin/1071__compat.py
openroot/bin/1073__json.py
openroot/bin/1075__path.py
openroot/bin/1076__proxy.py
openroot/bin/1078__resources_proxy.py
openroot/bin/1096_create_embedding_response.py
openroot/bin/1108_speech_create_params.py
openroot/bin/1115_chat_completion_assistant_message_param.py
openroot/bin/1120_chat_completion_function_call_option_param.py
openroot/bin/1121_chat_completion_function_message_param.py
openroot/bin/1129_chat_completion_token_logprob.py
openroot/bin/1146_translations.py
openroot/bin/1147___init__.py
openroot/bin/1148_chat.py
openroot/bin/1174__namespace_utils.py
openroot/bin/1179__signature.py
openroot/bin/1187_decorator.py
openroot/bin/1197__schema_validator.py
openroot/bin/1205_datetime_parse.py
openroot/bin/1219_types.py
openroot/bin/1221_utils.py
openroot/bin/1222_validators.py
openroot/bin/1225_connection.py
openroot/bin/1256__streams.py
openroot/bin/1257__subprocesses.py
openroot/bin/1276_tls.py
openroot/bin/1300_netstat.py
openroot/bin/1302_pidof.py
openroot/bin/1318_download_wheels_appveyor.py
openroot/bin/1320_generate_manifest.py
openroot/bin/1334_test_aix.py
openroot/bin/1339_test_memleaks.py
openroot/bin/1342_test_posix.py
openroot/bin/1344_test_sunos.py
openroot/bin/1350_dag_orchestrator.py
openroot/bin/autoupdate_loop.py
openroot/bin/local_rag_search.py
openroot/bin/0795_openroot_workflow_manager.py
openroot/bin/0807_Identify.py
openroot/bin/0812_Resource.py
openroot/bin/0816_Discovery.py
openroot/bin/0819_Resource.py
openroot/bin/0834_HMAC.py
openroot/bin/0835_Hashes.py
openroot/bin/0838_Proxies.py
openroot/bin/0842_X25519.py
openroot/bin/0844_AX25KISSInterface.py
openroot/bin/0845_AutoInterface.py
openroot/bin/0846_BackboneInterface.py
openroot/bin/0847_I2PInterface.py
openroot/bin/0865_rnpkg.py
openroot/bin/0868_rnstatus.py
openroot/bin/0870___init__.py
openroot/bin/0872_platformutils.py
openroot/bin/0876___version__.py
openroot/bin/0887_main.py
openroot/bin/0912__ed25519.py
openroot/bin/0932_make_unicode_property_data.py
openroot/bin/0937_sample.py
openroot/bin/0944_convert-pt-to-ggml.py
openroot/bin/0945_convert-silero-vad-to-ggml.py
openroot/bin/0946_convert-whisper-to-coreml.py
openroot/bin/0947_convert-whisper-to-openvino.py
openroot/bin/0948_generate-parakeet-test-model.py
openroot/bin/0956_english.py
openroot/bin/0970__events.py
openroot/bin/0974__state.py
openroot/bin/0978___init__.py
openroot/bin/0980_distro.py
openroot/bin/0991_test_cases.py
openroot/bin/0993_typing_objects.py
openroot/bin/1004___init__.py
openroot/bin/1010_color.py
openroot/bin/1016_error_wrappers.py
openroot/bin/1022_json.py
openroot/bin/1042__auth.py
openroot/bin/1052__types.py
openroot/bin/1054__urls.py
openroot/bin/1056___init__.py
openroot/bin/1060__constants.py
openroot/bin/1062__files.py
openroot/bin/1065__resource.py
openroot/bin/1072__datetime_parse.py
openroot/bin/1079__streams.py
openroot/bin/1088_models.py
openroot/bin/1092_batch_create_response.py
openroot/bin/1094_batch_retrieve_response.py
openroot/bin/1102_file_info_response.py
openroot/bin/1117_chat_completion_content_part_image_param.py
openroot/bin/1123_chat_completion_message_param.py
openroot/bin/1131_chat_completion_tool_message_param.py
openroot/bin/1141_function_parameters.py
openroot/bin/1143_audio.py
openroot/bin/1150___init__.py
openroot/bin/1154_mock.py
openroot/bin/1169__import_utils.py
openroot/bin/1171__known_annotated_metadata.py
openroot/bin/1172__mock_val_ser.py
openroot/bin/1181__utils.py
openroot/bin/1188_json.py
openroot/bin/1189_parse.py
openroot/bin/1192_arguments_schema.py
openroot/bin/1217_schema.py
openroot/bin/1208_error_wrappers.py
openroot/bin/1226_connection_pool.py
openroot/bin/1230_interfaces.py
openroot/bin/1232_anyio.py
openroot/bin/1233_auto.py
openroot/bin/1266__sockets.py
openroot/bin/1290__pswindows.py
openroot/bin/1295_free.py
openroot/bin/1311_who.py
openroot/bin/1315_check_broken_links.py
openroot/bin/1321_git_pre_commit.py
openroot/bin/1333_runner.py
openroot/bin/1341_test_osx.py
openroot/bin/1343_test_process.py
openroot/bin/1349_bottom_tier.py
openroot/bin/1351_meta_upgrade_20260805_000212.py
openroot/bin/register_pathway.sh
openroot/bin/unify_v2.py
openroot/bin/0794_ecosystem_dashboard.py
openroot/bin/0797_agape_engine.py
openroot/bin/0801_Broadcast.py
openroot/bin/0822___init__.py
openroot/bin/0833_HKDF.py
openroot/bin/0849_KISSInterface.py
openroot/bin/0855_TCPInterface.py
openroot/bin/0859___init__.py
openroot/bin/0861_rnid.py
openroot/bin/0863_rnodeconf.py
openroot/bin/0875___init__.py
openroot/bin/0880_sam.py
openroot/bin/0882_utils.py
openroot/bin/0895_helpers.py
openroot/bin/0904_KISSInterface.py
openroot/bin/0911_aes256.py
openroot/bin/0920_generate-encoding-data.py
openroot/bin/0940_server.py
openroot/bin/0941_convert-h5-to-coreml.py
openroot/bin/0952_eval.py
openroot/bin/0961___init__.py
openroot/bin/0968__abnf.py
openroot/bin/0981___init__.py
openroot/bin/0987_to_interpreter.py
openroot/bin/1013_datetime_parse.py
openroot/bin/1021_generics.py
openroot/bin/1031_type_adapter.py
openroot/bin/1040___version__.py
openroot/bin/1043__client.py
openroot/bin/1057__base_client.py
openroot/bin/1097_embedding.py
openroot/bin/1100_file_create_response.py
openroot/bin/1110_transcription_create_params.py
openroot/bin/1133_chat_completion_user_message_param.py
openroot/bin/1135___init__.py
openroot/bin/1138_function_parameters.py
openroot/bin/1160__decorators.py
openroot/bin/1163__docs_extraction.py
openroot/bin/1165__forward_ref.py
openroot/bin/1167__generics.py
openroot/bin/1182__validate_call.py
openroot/bin/1185_config.py
openroot/bin/1194_pipeline.py
openroot/bin/1195___init__.py
openroot/bin/1199__hypothesis_plugin.py
openroot/bin/1207_env_settings.py
openroot/bin/1214_mypy.py
openroot/bin/1218_tools.py
openroot/bin/1227_http11.py
openroot/bin/1228_http2.py
openroot/bin/1236_sync.py
openroot/bin/1248__asyncio_selector_thread.py
openroot/bin/1250__eventloop.py
openroot/bin/1251__exceptions.py
openroot/bin/1263___init__.py
openroot/bin/1265__resources.py
openroot/bin/1269__tasks.py
openroot/bin/1270__testing.py
openroot/bin/1271_buffered.py
openroot/bin/1278_sitecustomize.py
openroot/bin/1280_conf.py
openroot/bin/1282__common.py
openroot/bin/1293_disk_usage.py
openroot/bin/1294_fans.py
openroot/bin/1308_sensors.py
openroot/bin/1309_temperatures.py
openroot/bin/1313_bench_oneshot.py
openroot/bin/1327_print_hashes.py
openroot/bin/1329_purge_installation.py
openroot/bin/1335_test_bsd.py
openroot/bin/1337_test_contracts.py
openroot/bin/1348_test_windows.py
openroot/bin/cycle_recovery_v1.py
openroot/bin/faiss_search.py
openroot/bin/0798_agape_oracle.py
openroot/bin/0800_Announce.py
openroot/bin/0805_ExampleInterface.py
openroot/bin/0806_Filetransfer.py
openroot/bin/0811_Request.py
openroot/bin/0814_Buffer.py
openroot/bin/0829_link.py
openroot/bin/0837_Provider.py
openroot/bin/0839_SHA256.py
openroot/bin/0867_rnsd.py
openroot/bin/0871_configobj.py
openroot/bin/0874_validate.py
openroot/bin/0890_util.py
openroot/bin/0896_initiator.py
openroot/bin/0902_rnsh.py
openroot/bin/0906_SerialInterface.py
openroot/bin/0913_basic.py
openroot/bin/0933_make_unicode_wb_data.py
openroot/bin/0951_upload-parakeet.py
openroot/bin/0965__impl.py
openroot/bin/0967___init__.py
openroot/bin/0983_functools.py
openroot/bin/0984_itertools.py
openroot/bin/0989_to_thread.py
openroot/bin/0996___init__.py
openroot/bin/0998__exceptions.py
openroot/bin/1006_alias_generators.py
openroot/bin/1019_functional_serializers.py
openroot/bin/1020_functional_validators.py
openroot/bin/1030_tools.py
openroot/bin/1033_typing.py
openroot/bin/1034_utils.py
openroot/bin/1035_validate_call_decorator.py
openroot/bin/1041__api.py
openroot/bin/1053__urlparse.py
openroot/bin/1064__qs.py
openroot/bin/1077__reflection.py
openroot/bin/1083__utils.py
openroot/bin/1085_batches.py
openroot/bin/1090_batch_cancel_response.py
openroot/bin/1101_file_delete_response.py
openroot/bin/1107___init__.py
openroot/bin/1122_chat_completion_message.py
openroot/bin/1125_chat_completion_message_tool_call_param.py
openroot/bin/1127_chat_completion_role.py
openroot/bin/1130_chat_completion_tool_choice_option_param.py
openroot/bin/1142___init__.py
openroot/bin/1151_asgi.py
openroot/bin/1158__core_utils.py
openroot/bin/1164__fields.py
openroot/bin/1166__generate_schema.py
openroot/bin/1204_dataclasses.py
openroot/bin/1216_parse.py
openroot/bin/1223_version.py
openroot/bin/1237_trio.py
openroot/bin/1245_socks_proxy.py
openroot/bin/1246__asyncio.py
openroot/bin/1259__tasks.py
openroot/bin/1260__tempfile.py
openroot/bin/1262__typedattr.py
openroot/bin/1264__eventloop.py
openroot/bin/1283__compat.py
openroot/bin/1299_meminfo.py
openroot/bin/1303_pmap.py
openroot/bin/1319_download_wheels_github.py
openroot/bin/1322_print_access_denied.py
openroot/bin/1340_test_misc.py
openroot/bin/openroot_unified_launch_v1.sh
openroot/bin/pathway_chain_test.sh
openroot/bin/resolve_pathway.sh
openroot/bin/thermal_balance_v63.py
openroot/bin/router_relaunch_proof_v1.sh
openroot/bin/router_relaunch_proof_v2.sh
openroot/bin/agape_cascade/agape_cascade_diag.py
openroot/bin/agape_cascade/agape_cascade_sim.py
openroot/bin/agape_cascade/agape_cascade_v12.py
openroot/bin/setup_restore_v1.sh
openroot/bin/sync_validator.py
openroot/bin/simple_merge.py
agape_one.py
bridge.py
deep-scan-report.sh
groq_max_cycles.py
agape_clean.py
heartbeat-status.sh
openroot-deepdive.sh
setup_openroot_phone.sh
une_client.py
test_une_full.py
agape_slim.py
launch.sh
observe.sh
run-command.sh
start-volumetric-llm-node.sh
ghost_fix_v1.sh
wireguard.sh
faiss_search.py
run_nomic_embed.sh
push_openroot_readme.sh
push_profile_readme.sh
push.sh
audit_repos.sh
raise_to_6n6.py
start_llm.sh
batch_nomic_embed.py
find_original.sh
find-128g-usb.sh
groq_fallback.py
phone_check.sh
one_principle_n_power_n.py
newton_chain.py
local_rag_search.py
agape_hierarchical_raising.py
lattice_cli.py
portfolio-audit.sh
openroot_launch.sh
openroot_full.sh
openroot_fix.sh
deepdive.sh
fix-secrets.sh
fix-license.sh
stack.sh
run_rampup.sh
push-openroot.sh
openroot.py
mdpipe.py
diagnostic_check.sh
test_phone_tasks.py
enhance_tasks_with_efficiency.py
fix.sh
start_full_embed.sh
bootstrap-node.sh
repo_audit.sh
.une-save.sh
phase1_audit.sh
apply_fs_hook.py
fs_hook_patch.py
openroot_deploy.sh
agape_init.py
cleanup_and_backup.sh
constitutive_voice_engine.py
openroot_claude_pointer.sh
constitutive_compiler.py
fix_chain_verify.py
openroot_hub.py
agape_frequency.py
agape_neurogenic_kernel.py
agape_setup.sh
filescraper.sh
agape_evolution_v2.py
openroot_archiver.py
unified_agape_engine.py
relay_probe_v2.sh
relay_v3.sh
relay_arm_v7.sh
repair_une_syntax.py
fix_une_and_commit.sh
commit_une_syntax_clean.sh
repair_all_une_and_commit.py
emergency_fix_all.sh
openroot_unify.py
compressor_node.py
core_engine.py
fix_last_une_error.py
ride_along_v1.sh
hive_swarm.py
apape_net_setup.py
map_files.py
inspect_map.py
build_coder_environment.py
v7.py
swarm_bench.py
smoke_fix.py
post_launch_triage.sh
triage_followup.sh
vault_status.sh
openroot_termux_recovery.sh
openroot_branch_resolution.sh
issue_triage_v1.sh
dup_cleanup_v1.sh
forge_rename_fix_v6.sh
or_docrefresh_v1.sh
kai_extract_v2.sh
lumo_courier_v1.sh
hash_assign_v1.sh
A1.py
hash_manifest.py
relay_report_v9.sh
relay_roundtrip_v11.sh
relay_package_v15.sh
relay_autonomy_probe_v18.sh
relay_autobank_v22.sh
relay_autobank_v23.sh
openroot_credit_tracker.sh
openroot_finance_tracker.sh
scheduler.sh
find_api_keys.sh
joule_leverage_analyzer.py
snapshot_bootstrap.py
backup_to_usb.sh
patch_voice.py
termux-hygiene.sh
agape_farm_os.py
une_max_efficiency_lang.py
une_atomic_library.py
sacred_geometry_agape.py
agape_kernel_v2.py
agape_ledger_chain.py
und_protocol.py
agape_node_bootstrap.py
agape_primitive_forge.py
une_closed_loop.sh
final_une_syntax_pass.py
emergency_syntax_fix.py
diagnose_and_fix.py
diag_fix.py
surgical_fix.py
final_fix.py
fix_final.py
fix_exact.py
agapenet_unified_setup.py
storage_daemon.py
fast_backup_daemon.py
agape_net_setup.py
agape_net_full_integration.py
openroot_thesis_one_shot.sh
index_content_blobs.py
une_fix.py
fix_kai.sh
usb_flash_import.sh
openroot_tailscale_ssh.sh
orchestrate_team.py
repo_hygiene_gate.sh
ts_check.sh
update_goals_final.sh
forge_run_a15_v2.sh
forge_fix_base_v3.sh
forge_targets_fix_v4.sh
forge_full_ship_v5.sh
setup_this.sh
kai_extract_v1.sh
ride_along_v2.sh
phi4_router_v1.sh
seed_to_markor_v1.sh
orbundle_stage2_compose_v2.sh
orbundle_stage7_finalize_v2.sh
finish_loop_v2.sh
agape_thermo_merge_v1.sh
joules_counter_v1.sh
consolidate_state_v1.sh
complete_arc_v1.sh
openroot_replay_gate_source_v1.sh
openroot_extract_audit_only_v1.sh
openroot_double_cache_probe_v1.sh
openroot_preserved_pair_replay_v1.sh
openroot_commit_experiment_snapshot_v1.sh
openroot_github_intake_compat_v2.sh
openroot_intake_reseal_rerank_v3.sh
openroot_intake_deliver_v4.sh
agape_multilingual_drift_matrix_v1.sh
check_ancient_source_words_v1.sh
life_giving_ancient_roots_v1.sh
grep_symbols_v1.sh
fix_loader_type_v1.sh
push_and_emit_seed_v1.sh
cross_window_reconcile_v1.py
gh_branch_audit_v1.py
gh_branch_review_v1.py
rk1.sh
rk_final.sh
rk_push.sh
compost_lookup.sh
nomad_recon.sh
nomad_recon2.sh
nomad_build.sh
nomad_fix2.sh
disk_truth.sh
eta_audit.sh
eta_gamma_finalize.sh
gamma_direction_fix.sh
openroot_promote_acre_ledger_v1.sh
openroot_acre_bak_diag_v1.sh
openroot_full_coverage_fix_v2.sh
openroot_harvest_gate_v1.sh
openroot_nomad_delete_v1.sh
emit_window_seed_v2_fixed.sh
openroot_partial_hunter_v1.sh
openroot_treasure_recon_v2.sh
openroot_watchdog_and_sweep_v1.sh
openroot_partial_ledger_census_v1.sh
qh_v1.py
openroot_newton_resolve_v2.sh
openroot_pod_data_inject_coder_v3.sh
openroot_docsearch_gt_coder_v2.sh
event_seal_and_scan_status_v1.sh
ledger_ssd_backup_v1.sh
unified_final_merge_v1.sh
unified_evidence_800k_builder_v1.py
openroot_unified_evidence_800k_v2.sh
openroot_unified_evidence_800k_v3.sh
unified_evidence_builder_v3.py
openroot_import_a15_v1.sh
openroot_command_ledger.py
bg_process_check_v1.sh
audit_recent_commits_v1.sh
word_census_v1.py
pod_garden_bootstrap_v2.sh
openroot_garden_repair_dilute_v1.sh
pod_per_repo_clean_build_v4.sh
mesh_zone_fix_v2.sh
mesh_dossier_engine_v1.sh
router_gb_install_v1.sh
router_gb_install_v2.sh
router_gb_install_v4.sh
router_benchmark_gate_v1.sh
router_gate_run_v2.sh
recover_v1.sh
find_recent_ai_loop.py
deploy_to_jesse.sh
relay_resume_v5.sh
relay_acceptance_v13.sh
relay_finalize_v17.sh
relay_report_bank_v19.sh
relay_report_bank_v21.sh
embed_patch_v1.sh
merkle_lineage_v1.sh
emit_window_seed_v1.sh
orbundle_stage6_guide_v2.sh
agape_stage1_genesis.sh
agape_stage2_run.sh
create_query_wrapper_v1.sh
fix_merge_v2_rebuild.sh
inject_joules_badge_v1.sh
joules_badge_multi_repo_v1.sh
nomenclature_seed_v1.sh
check_bash_history_v1.sh
openroot_recovery_search_v1.sh
openroot_core_manifest_v1.sh
openroot_energy_core_contract_v1.sh
openroot_commit_scope_v1.sh
openroot_main_sync_gate_v1.sh
openroot_existing_index_intake_plan_v1.sh
generate_nomenclature.py
patch_euclid_loader_v1.sh
grand_unification_loop_v1.sh
run_unification_proper.sh
save_and_verify_seed_v1.sh
emit_full_seed_v2.sh
final_sync_check_v1.sh
eta_executor_batch_v1.py
eta_executor_correction_v1.py
gh_branch_final_v1.py
lost_file_restore_v1.sh
rk2.sh
rk4.sh
rk6.sh
mistake_restore.sh
eta_dump.sh
eta_commit_push.sh
openroot_agape_acre_inspect_v1.sh
openroot_acre_v2_canon_v2.sh
openroot_a15_hash_audit_v1.sh
openroot_cross_device_final_scan_v1.sh
openroot_update_state_pods_v2.sh
openroot_update_state_doctrine_v3.sh
openroot_update_state_doctrine_v4.sh
openroot_nomad_cleanup_root_owned_v1.sh
openroot_partial_ledger_census_v2.sh
openroot_tri_status_v1.sh
openroot_census_inspect_v1.sh
ask_pod_v1.py
openroot_pod_era_v1_ship_v1.sh
openroot_safe_handoff_v1.sh
ghost_script_audit_v1.sh
ghost_recon_v1.sh
ghost_commit_v1.sh
openroot_ultimate_plan_persist_v1.sh
openroot_interaction_access_seed_v1.sh
openroot_evidence_reconcile_v1.sh
openroot_bank_768k_receipt_v1.sh
openroot_pod_skill_v1.py
find_gh_docs_pod_v1.sh
seal_audit_debris_v1.sh
pod_garden_bootstrap_v3.sh
dossier_snippet_and_seal_fix_v2.sh
dossier_kw_compile_v5_ship.sh
pod_per_repo_fix_v2.sh
smart_router_test_v1.sh
mesh_dossier_fix_v3.sh
router_gb_install_v5.sh
openroot_alligator_trace_v1.sh
fix_selfchurn_v1.sh
commit_state_hash_patch_v1.sh
handoff_seal_v1.sh
save_script_protocol.sh
orbundle_stage3_setup_v2.sh
stage_commit_push_all_v1.sh
queue_update_v1.sh
agape_genesis_v1.sh
fix_bridge_format_v1.sh
instrument_self_accounting_v1.sh
agape_thermo_merge_v2.sh
governance_seed_v1.sh
gh_cache_rapl_v1.sh
openroot_core_contract_extract_v1.sh
openroot_miss_summary_v1.sh
openroot_rights_energy_gate_v1.sh
openroot_reconcile_handoff_v1.sh
openroot_finish_closure_v2.sh
openroot_intake_deliver_v5.sh
openroot_intake_promotion_contract_v1.sh
openroot_apply_index_plan_v1.sh
check_nasb_resonance_v1.sh
find_postulates_json_v1.sh
deploy_engines_v7_safe.sh
test_engines_v7.sh
agape_nomenclature_v1.sh
block_1_nomenclature.sh
commit_and_push_loop_v1.sh
embed_agape_universe_v1.sh
git_audit_v1.sh
eta_rank_engine_v1.py
gh_survey_cached_v1.py
gh_branch_diag_v1.py
gh_lost_work_recovery_v1.py
rk5.sh
mistake_rescue.sh
mistake_dump.sh
mk_ci2.sh
close_session.sh
nomad_fix_and_verify.sh
eta_fix.sh
openroot_acre_ledger_repair_v1.sh
openroot_acre_ledger_repair_v2.sh
openroot_acre_recipe_probe_v1.sh
openroot_acre_final_repair_v1.sh
openroot_acre_fix_dest_v1.sh
openroot_acre_value_audit_v1.sh
openroot_eta_gamma_cinema_v1.sh
openroot_acre_v2_canon_v1.sh
openroot_a15_hash_universe_v1.sh
openroot_index_census_v1.sh
openroot_nomad_mysql_probe_v1.sh
openroot_treasure_recon_v3.sh
openroot_pod_launch_v1.sh
openroot_census_resume_v3.sh
openroot_pod_resume_v3.sh
openroot_overnight_v1.sh
validate_newton_append_v2.py
openroot_pod_era_v1_finish_v1.sh
openroot_pod_era_v1_finish_v3.sh
openroot_unblock_and_coder_docsearch_v1.sh
openroot_surgical_model_ingest_v1.sh
openroot_safe_handoff_v2.sh
unified_clone_merge_v2.sh
a15_shared_corpus_v1.sh
openroot_readme_commons_draft_v1.sh
unified_ledger_profile_v1.py
unified_ledger_builder_v2.py
openroot_filemap_inventory_v1.sh
import_a15_into_unified_v1.py
openroot_session_mega_v1.sh
openroot_stack_tiered_bench_v1.sh
dossier_kw_full_v1.py
dossier_kw_full_v2.py
dossier_kw_full_v3.py
pod_garden_bootstrap_v1.sh
pod_tier_spine_v1.sh
dossier_recon_and_fix_v1.sh
pod_per_repo_fix_local_v3.sh
pod_per_repo_build_v2.sh
micro_model_fleet_v1.sh
mesh_zone_gateway_v1.sh
heartbeat_mesh_integration_v1.sh
router_gb_install_v3.sh
openroot_loop_question_receipt_v1.sh
deploy_to_jesse_robust.sh
relay_verify_v6.sh
relay_release_probe_v14.sh
relay_reconcile_v16.sh
relay_report_bank_v20.sh
semantic_routing_v1.sh
backup_emitter_to_repo_v1.sh
orbundle_stage1_dockerfile_v2.sh
orbundle_stage4_readme_v2.sh
orbundle_stage5_index_v2.sh
fix_agape_merge_v2.sh
fix_merge_and_create_v1.sh
nomenclature_trials_v1.sh
a_definition_resonance_v1.sh
a_definition_multilang_v1.sh
verify_loop_metrics_v1.sh
fix_pathways_schema_v1.sh
trace_history_v1.sh
inspect_window_seed_v1.sh
resonance_nasb_multilang_v1.sh
openroot_baseline_inspect_v1.sh
openroot_today_phi_receipts_v1.sh
openroot_audit_baseline_contract_v1.sh
openroot_cache_miss_diagnosis_v1.sh
openroot_close_recovery_loop_v1.sh
openroot_commit_push_closure_v3.sh
openroot_github_intake_rank_v1.sh
openroot_existing_index_writer_contract_v1.sh
nasb_kjv_agape_drift_v1.sh
bootstrap_agape_kb_v1.sh
test_euclid_loader_v1.sh
deploy_engines_v7.sh
agape_dense_nomenclature_v2.sh
fix_loader_robust_v2.sh
block_2_geometry.sh
block_3_seal.sh
test_full_pipeline_v1.sh
complete_convergence_seal_v1.sh
embed_agape_universe_v2.sh
rk3.sh
stage_and_commit_audit_v1.sh
push_and_sync_all_v1.sh
pull_and_push_une_v1.sh
rebase_reconcile_v1.sh
compost_inspect.sh
nomad_integration_analysis.sh
nomad_inventory.sh
nomad_recon3.sh
admin_diag.sh
gamma_audit.sh
eta_gamma_search.sh
gamma_deep.sh
eta_gamma_complete.sh
eta_gamma_fix_branch.sh
openroot_agape_acre_lookup_v1.sh
openroot_acre_chain_verify_v1.sh
openroot_acre_forensic_v1.sh
openroot_acre_verify_commit_v1.sh
openroot_full_coverage_fix_v1.sh
openroot_a15_hash_audit_v2.py
openroot_update_state_pods_v1.sh
openroot_hidden_work_hunt_v1.sh
openroot_nomad_delete_v2.sh
openroot_nomad_cleanup_root_owned_v2.sh
emit_window_seed_v2.sh
openroot_treasure_recon_v1.sh
openroot_pod_builder_v2.sh
openroot_pod_flock_v4.sh
openroot_census_inspect_v2.sh
openroot_query_harness_v1.sh
openroot_gh_announce_v1.sh
openroot_newton_resolve_v1.sh
validate_newton_append.py
openroot_pod_era_v1_finish_v2.sh
openroot_surgical_model_ingest_v2.sh
full_ledger_audit_backup_v1.sh
unified_ledger_merge_v1.sh
openroot_unified_ledger_merge_plan_v1.sh
openroot_unified_ledger_v1.sh
unified_ledger_builder_v1.py
openroot_unified_ledger_v2.sh
openroot_unified_evidence_800k_v1.sh
unified_evidence_builder_v2.py
openroot_commit_architecture_drafts_v1.sh
openroot_a15_ledger_inventory_v1.sh
openroot_local_model_command_ledger_v1.sh
superloop_quarantine_diag_v1.sh
word_census_v2.py
census_and_coder_v1.sh
pod_chunk_hash_upgrade_v1.sh
pod_per_repo_build_v1.sh
mesh_dossier_prove_v2.sh
openroot_pod_init_v1.sh
rollout.sh
bg_process_check_v2.sh
terminal_forensics_v1.sh
dossier_kw_compile_v4_ship.sh
dossier_kw_compile_v4_1_ship.sh
pod_per_repo_fix_local_v2.sh
openroot_receipt_install_v1.sh
install_openroot_query_v1.sh
bin/pplx_relay_v1.sh
bin/pod
.local/bin/httpx
.local/bin/openroot-query
openroot/bin/goals_rebuild_v1_20260920.py
openroot/bin/goals_rebuild_v2_20260920.py
openroot/bin/goals_rebuild_v3_20260920.py
openroot/bin/todo_processor.py
openroot/bin/onepass_v3.sh
openroot/bin/push_guard.py
openroot/bin/stack_gate.sh
openroot/bin/packet_query_v1.py
openroot/bin/find_green777.py
master_codebase_orchestrator.py
OPENROOT_EOF

cat > "$WORK/manifest.sha256" <<'OPENROOT_EOF'
79aefcd519188ab5f38e5db873e07e109e3f25c9ebb4534539eb8d837ff98ef8  bin/ledger-append
48988519c2750e35df319595ca9494dd4417d1c32cbfa3aa64b1a2de18c2d8fe  bin/say
59b50a493bccdbacccfba860759d0cbcbe28b7c4a4a2f4aa96c322d003257430  bin/ask
3efc4aba22445812291dbff1f23ccf8418f09a6c2582d844030351f093509e7d  bin/deepdive.py
fde2bc69c98a14542e4d61ea13905a6d544c4572ae0b9a6f4e0c6348555d3778  bin/audit_repo.py
d085ffd6166dd8a3bda970ff8c75ef0c68a13aebe95e606b5ac399c0020f5683  bin/aider-lite
706852523f2d47640c16da4a570f8bd96108a32cfe4b866ba7f47c87ec139475  bin/verify-chain
1571ea7263f44c76ddb55b8644bf06d5ab6140d9f5cfd48f798fd31948ee9809  bin/fix-chain
9d7db06e1f196fe9dd151323eabcf9413997647c0ff86807e97e3039a3a585d6  bin/sol-anchor
cf25ea120446c2da06ed93672f3d7af0fa8c5bf86fa8bc7210c946ca3a21896b  bin/measure-drain
0db1c5e87b2b58529a90a92cc725ec65ad6e3009e2fcc623b223127bdb3f8979  bin/acre-dashboard
7106f989cd42a769ec78583c643716786dc94926f395bc329f7293105c01adf7  bin/thermo-audit
1ce4e39207461e6be95237a393e4839dd618661b3f94c49f99fa7df52eb12262  bin/hive_entry.py
9b17b26ea924788a5bd7274a47f77e08ab83546a5e83d6dfe4e033c6a72ff51e  bin/relay_exec.sh
9c9ee0f20f2104f1d3f1f526ae824389be5df0f78d74637e94e478c0b1f84391  bin/cycle.sh
fd17fb023b80fef27ba0456ce43a9b4811137dd5ea2493cbeea814b5cbc97fde  bin/sys_snapshot.sh
a2c9919d25ac33d92e182b577865db0b4e5006cbdfc633ee093a494281765ca6  bin/wealth_log.sh
15ed208639be55b4268c2e1131d871fd74c4f0bb7a558954fb4cd645e62d2ec4  bin/ots_anchor.sh
a4e89db9891823d3b3aa0c0d127d8af4abecb4e980584bdb62b668c37ada7b95  bin/structure_enforcer.py
4738818f96529746e2d2251c1facff9d98c88b5ad1f49b49407eff29102350d7  bin/immortal_context.py
dd25fa8c4a0f7afaf041619eec380bf88eb5d662ffc5be763161dc6a9ed59962  bin/openroot-status
a851b4b70c2541ef33cd407d8f478f67cc53ea91d65867d3167b782f900471e8  bin/aggressive_dedup.py
68b3e3ca371cc705cd8a256d197ffabefaed6609dd93b886585b9bbf6562da93  bin/backup_nontext_to_usb.sh
fe061b3587cc82518b7e6235acb61d738d700a49336d2738214748812041ecbf  bin/move_home_sd_to_usb.sh
003a374a407a4b02fcd208c8d14b10a20352aca47914e6685b88c37cb3d6f42d  bin/clipboard_watcher.sh
c8a103652eda424d4dc12f867745683a751dac016ca2fa656beec448dcae46d1  bin/agape_fusion_loop.sh
3117a85498d4d917f5edfc50cdefeda816ea443489cbc9a27a187c6cb96764bf  bin/termics-compound-watch
c3f93796990aba4b77007c93fb500ccd1b3bfb1d2dbf71f87e177e0e0d7e47fd  bin/termics-bridge-any
15ba6f01d5d34f2620f9c26cd73398d3e20f28d92e0d36e9395e1cbc37695dba  bin/termics-mark-mistake
e7352f180d7fc61eee3489fbb873257cbfe5a8faacfa7c12f2db1b9efdfdaf09  bin/termics-ledger
4d89bf97a57cb2f1f5c12325ee8b138f13c6028b55c762151e613d591270ed3e  bin/termics-capture
eb0b90c0f1433fbb412827c03f1f539b778d5e6f8a0ea7946515bcf6799ca791  bin/openroot
b844ed72762552f34d20cf96ef41027ef3a0088e7da85d8be50362cad733db3a  bin/openroot-inventory.py
1c78dbb695c8e5196a18dead8fb27255f3673e18c2cfe2b542b23eca2ccc514d  bin/openroot-run
ae919a7c76b738b412af041c97e7cb92140a063259981653235e4b64f7e7a510  bin/openroot-absorb
3000ea83e36630e38304309d2da51dd8f1bf0800bcb98cbf2deabb91b861beea  bin/openroot-lattice
21af68057d6977317035fdae709c5ae9ee8958afaf2f6cef952578ac6a938144  bin/openroot-keyword-scan
8d51113d3c696c1673d2bc152c6bc4774a2ffb177e29cf01f22974e3991fd49e  bin/thermo-snapshot
c3aaa874f63a5b774eb0c5b4c44cb2f843874ea68d19825c52eb2b1925463a16  bin/bridge.py
b93f478e7e7f72f2ed3233e83871299fab99b263eb36d3e26f7fa0ed3af8a612  bin/stctl
79c15e3f0651a56a91759f93f69cb965cf3bc6bf86a347d16572d0e6128c963e  bin/rcstatus
9c8590bcade7500c05064e17f1877795d0829fb646f2006cd2d0f1a36f66ac84  bin/st-heal
aec98789f74f92f5bdefd0d526605e0c694b7ac47b41ee016a782a8ca6dd5b2d  bin/st-folder-opt
ab07da7a346f38afab465081115dbe38e805783b3fb8ca4989fa645f6ccda473  bin/une_master.py
1eaf89a3924adf2cc2bc0c040b196a8a8e2e14285abee439f357412ee9e72d16  bin/openroot-foundation-v3.sh
78747c40ae7e7136e43505b0cad7c1d04287733932189bec3bdf873d709a39c7  bin/or-status
c79d63ab380495931efd9ee0c79e3f43adab89447e223ce11c23e474ac37afdb  bin/or-sync
eced89e335b8e9f3f8b850a424c7eae5b08f06734d3caa695cb8700a64e955e9  bin/or-syncthing
685820846f3173dab26fd83d0d7e97218d194dc51c57b135aecf93e265bb1a0f  bin/or-resume
7e78302ba2695ed39e200d30c06679d81bf6967e592a4e8b7490d7139228885c  bin/grand_unifying_script.sh
9449fcced2a2a779d6531c27eae6daff3015699fe615186cdbafb3bed3a04b7e  bin/or-oracle
85f1fe4f0d3dcf29b8dc59efaab610ace59b732a15aacf71707662abdc697880  bin/or-learn
14b65a85501b2839c3524f9382a227ed974e05e48f48f83bd2efeea58e1461d5  bin/or-nodes
ec4198edece220df3cc487e3dab1be39f160461b7873271c7db6979e568ee5c3  bin/optiplex
53585d565fd5252ac1019f79415af05eb46372788f6c01d21d472e35be052f96  bin/or-coder
1239cf17d6e83579b68ebf52bd6bccb7516591455d716520bfabd65d3099d2b2  bin/stack_gate.sh
8fcff934cce28942b384bec1211ba7aa85d965f1bc068f8f0ee61f899188076e  bin/a15_copy_symposium_from_download.sh
8d88940484edd9ed7abf4c15f2faffc58d89fe5199146ecf149634df070208c5  bin/find_green777.py
50ec32d4a484ff05a3925a3d36be63ff914260830a662a82ffe21e1f8682b5d8  bin/a15_offload_v1.sh
1343d0c7c94937203fd5bfcc7f2d6f5aa34f7cf9f82b837607855ac7d05db1a5  bin/termux_clean_v1.sh
ae99f44fcbfe1b581193d9371c391bbdc4896b860f8939176b03f6346fe0dd6a  bin/openroot-diff
cc671b22a8d70f4ace3efeb169404a8b21294c8325b581ded31543edcc0a687f  bin/openroot-safe-stage
b5ab235d58e505aaa7147c7959eab0fb1b9ffb2ab5aece39016469ca7a849ce9  bin/lumo_send.sh
279d904612cc7a60a32034407f0b6cb5a7fdd147cc38a62131959f4af5410d6f  bin/lumo_flush.sh
67b7eb3ec52cc6c84841d296d0892cd2d0f48bf0c96a5002afcae4cb9e1d3222  bin/file_access_hub_v2.sh
9be9a47338741bd3da2b9d59ad31384c2dddd7383bfbb5576f40ecdd5ce7f0e2  bin/lumo_clip.sh
30a30e1f049f782466907b7575bc7a35d4991d0680aafa257042d427e50c1b34  bin/fetch2clip.sh
59f6ffdec60fc4953781556eef8f1fa4caf200eacf9a881dab1153ebe4c0997b  bin/ai-check
6bc78571f8b66a816757a2549df45173cb2ef358e9beafac0b7d581deb5c0980  bin/a15-runner-v1
7f6aeefa303b53b9a44ab953400c88ef155336f6787acc00cdf4d84944031587  bin/a15_deepdive.sh
f87ae8465033bbf9ff89e48f98c300a57e0c940e6c58c740f6e1a2dfcb553192  bin/a15_inventory.sh
f30f07c7e5d45deb680cffc36e752343ae514c0accdfa108ac71bc00c080808d  bin/dedup_reclaim_v1.sh
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  bin/a15_inventory.sh.tmp
0c3957d6fd3b820ec896ad4c72423b7f52af892b5dc889be046ffd0511a2a740  bin/dispatch_optiplex.sh
daa93b91ab389554338a202b9378219014f28856f9209c22a2b6551d407e9199  bin/beat.sh
ae3a2972da1e0a2995b6e7013dcdacf26fbdb7a47ad716d539b5867658083f05  bin/podpush.sh
23939eb17c1832b5ba74f000dd10fc648cb7e79126e2390ddc26bc24ac31f793  bin/orphan_rescue_v1.sh
e97d9f0371977293d0672a14ecbc0fb8ea0a6d28cbe6d64c59510a1ca52309bd  bin/orphan_transfer_v2.sh
c743793cf50aea6f52ed348ba2d184e533aa21de4afeb2620f8c86ac516f176f  bin/orphan_transfer_v3.sh
1d2176d143d418bf2152706ffc50035e03f8249228824de39ff888dfa6ca1c99  bin/promote_top10_orphans_v1.sh
12d895304bf6776644143996d59aeca514aea8eff636ef4129ac3c809e80e34e  bin/promote_top10_orphans_v2.sh
10a5d85c34dec66c276136a26949aded3a182d89a82977f357310fb47c19091e  bin/pr_squash_survey_v1.sh
0ea91990cf5bbf57488c971af49a46f2d7891a907d29f4b52e4f48be9976c476  bin/pr121_squash_v1.sh
8bab1ec59c4591e2129130daca1d7e17eda4263daaa72c713e162a3cd1a5d6a7  bin/secret_scrub_v1.sh
e8bfbc105551808d5f5afb781f35a64f87d3c8383b9ed20c457e14d8f98b896e  bin/openroot-ask.py
48f826969c3a6d4bdd8ab1b03ed3c64778d1c0307ff6bafba2180449ab965b18  .local/bin/llama-server
1cfb734801dce2112f9d58fb000c525ececc2d4d7e3b093f0b458ad37d3468ff  .local/bin/llama-cli
e91d12e9e73bff2c66985cb4aed91ede932c470447f56ce36034e5859f621e89  .local/bin/rish
3736b628641e5c402f127c94fc252e7d82a48e732c31e5f474790b1123655d20  .local/bin/tlog
d7d098bff72a269f68e777cbab1e1fb83ef66aebb86e0453e556897d18b42f4b  .local/bin/clip
04c6695c4ea7edcb6b3f20cccd1cdfaf6eaa4c6d51d4c7ded4e082e3e5b2fc87  .local/bin/distro
bfa5f531c48e30e73247fe74b112fdd4b25e61247bfbfa2500c0fc665106c7a8  .local/bin/compost
ac523e34d0964e02cbde3974db807dd7a875d2fed9dd42e5f268b4b79de17e2f  .local/bin/bridge
28642476c4c71bdb0ae45064f39c83c88562e491d827708fb5139ec0475b17a9  .local/bin/openroot-query.bak.20261019T055235Z
cc62a6daf519899cf4bd3f7974af845d45e7e00082e42a4a2e00c0cb49010080  .local/bin/openroot-query.bak.20261019T060846Z
2717335bf6700a10b7fcd7cc4492d8da211066c3afb0ad9a5ae7b7ac3fe0046f  .local/bin/<TOOL>
2717335bf6700a10b7fcd7cc4492d8da211066c3afb0ad9a5ae7b7ac3fe0046f  .local/bin/<TOOL>.bak.20261019T083044Z
339ed4dc9489971dae42c6b1ab36f33350136c16e1486e8a1e41423a5dcce3d4  openroot/bin/recall
ef99527f6a5d7e2e81b8d012d1896f55550d150dc1e8c3b0d78a83cfa6adc40c  openroot/bin/rescue_a15_unique.py
86141558da0b7d8aa934a79fac42ed97b4d7908e601bb8f3371afef8f948eec9  openroot/bin/relay_v1.py
fc67248798b80851e2c0e84eaaa3e9ce159cf3893ec7c7526bf924e8d975a6f0  openroot/bin/compound_v1.sh
9f0eb9220756268d36b8f216d6ff1bf0dfebcde959f7427d60c8f6ee5fd4a356  openroot/bin/relay_v1.py.bak
0eb1bfe371d07d78e772dacb904928feee627572313ddf3a9d832ca133bd2449  openroot/bin/gh_audit_v2.sh
a8fcc3916e97cdbcddd7e9380dc898e4305c82671e62a3eac18cede79d70fba7  openroot/bin/mobile_audit_trigger.sh
9a7c7fa8b7a6d3a8bb26abdb45b29da9fdddd0d522ec8763b2e343a2fdafff51  openroot/bin/hygiene_fixes_v1.sh
978ddc061f296e262703858ceac4644d5082eb459140c6f318fdba8548384d75  openroot/bin/hygiene_fix_driver_v1.sh
24570e61bcb317cc813cf397ceb030d3bffe94fcb76565465eb3e67fd465c818  openroot/bin/need_gate.py
d5387ccfce576f5158a54012d8ab4ef96c1f4f46a5700aa0c761dc53f13d71ed  openroot/bin/h003_log.py
674c8d3e53e2ebf17d0ce97cabaafa1a82a558c215c10a79eeb3151f5d24e12c  openroot/bin/popw_hang.py
d6a4560741b792c39878dd40e06d47357e2e9e8646e518aa7a5c2f8c86ac0577  openroot/bin/triage100.py
cf3ba0e08a2b5e20b7f8995919a0c1e9881d75797d875d18b5df1dcce98c2dd1  openroot/bin/run_triage.py
13a36b74bce753453df684ce587dd1cc1ff458a947025ccb3718414e2e794167  openroot/bin/openroot_master_deploy.py
9c782e6a20a4aef81bf1f2108dfca537763da9ccd2fcf60d573de6b15b8e31d5  openroot/bin/sync_to_optiplex.sh
f7fe8a44cb837db95fe272efec4288f49e810b7fd395dc295877f2b0382c0399  openroot/bin/abstract_grade.sh
d9f49872193262d10ce281e47a1f574aee32121376f4c771dfd4125650000ba3  openroot/bin/agape_node_bridge.sh
cd55122b35c21314e43c742602e9dd091bc0999601106b94af418d29d8cda1c1  openroot/bin/agape_qa_engine.py
d17fae84459f642439f24e49da83af96fd4841c4fb6811512e501df56f19a5d3  openroot/bin/asset_assign_pipeline.py
2e8d2f16c57e63590db9d40523ec362cb8a9376faadd382ff7ac2531d31419a4  openroot/bin/asset_preclassify.py
582ba2794e4e1bb01a58b3d06548359ddc5effc75c3d2ffa432370e3ec9e5808  openroot/bin/asset_preclassify_v2.py
717fe8b4ac2e09d73e83a4d15890480bb73cbc97593b86425a07cee48c1fde20  openroot/bin/boardroom_router.py
24e5bc40a446d96c43717f3f5950c4c4a2f7cddd969b8ca2c91c5edf7873f7c0  openroot/bin/build_core_view.py
811041e5f7b81537da5191a4edf30fc8bd0f6fa443dc4ba3709592415f14eb36  openroot/bin/core_view_server.sh
e515c5ef561d60074a983d9e098818977c13def6b993711842c6cced2cc72726  openroot/bin/cosmo_rack.py
edd1941beb1c5f88885c6637093222afbbba3adce54bf8634b18167099b1ace0  openroot/bin/daily_loop_v1.sh
5e9158b3beb29138621dd64118516db91ab407cce0d5e985f8043513e031bda0  openroot/bin/db_recon.py
ce022af672dc9000207138f23896579879f7f30a053cf806046dc476da19312f  openroot/bin/db_tune.sh
aeaede1bea874d7d8261452571fe7a8da65813876bf578e3a1e207ae693e9b0c  openroot/bin/embed_index_v1.py
7c10457d14017ede5e61482173fe3a25a91181c3f390dc7a4207b169e840f314  openroot/bin/fix_planetary_math_commit_v2.py
95dfc3665eb30be25f0d1e845160ef98739e828d94998130636301b69e5a057b  openroot/bin/fix_planetary_math_v1.py
892bae8f302152153f8a759756ec94c68fef30b946fa74385c12325620fa97d9  openroot/bin/fleet_check_v1.sh
cb208d1c84e82ec336bfac70b2419a578198904f04b383b237ee64c91f309f00  openroot/bin/fleet_closeout_v6_20260920.py
d3527c716ae709641b701af4f9161636018a5208d1b2a5d2f99974229f990f0e  openroot/bin/fleet_snapshot_symposium.sh
fa7c643093f108f3c884a713567b169b212dc0caab9059fec224b994287d7222  openroot/bin/force_merge_push_v1.py
949e4be6372bd10ae75edf1801a8307158ef1ab5f609597c5112eb539ca912da  openroot/bin/frp10_probe.sh
4f5bda8db99e4ed27fd5ca6fdfed78bc413cefd9d860fb6ffba9adb5ffb44a22  openroot/bin/frp11_forensics.sh
d1e5875f32cbcc91f510e43e48e0bef3a005b54e2f8c66fd18d4f0fcea25a1b2  openroot/bin/frp12_execute.sh
05ae4dc695e2311041c041e3948af07420adcbb9c400dbfb2ea8c993fb58bed2  openroot/bin/frp5_deep_audit.sh
2b93f4f4a9120aa0eb004c79e2d4ed307e8e86a8193d90549a05be39485fc54a  openroot/bin/frp6_fleet_squash.sh
2e32f20982de702cd96292d2ec3448664d65353f3d837b92c809123a9818f2fe  openroot/bin/frp7_triage.sh
deec7d65e9d9d2fb3591bab589238ef9926050f714392e235bf1a01f55f256f9  openroot/bin/frp8_prune_classify.sh
29e0b0763697177501aad0444f94ad0fb2a53646e10017745c168ff57ea70995  openroot/bin/frp9_tree_dedupe.sh
2a9c86d1a633d8f0bd0c47405ab32b59d58b1c244a6c9b3520f932a9712c3dfe  openroot/bin/gh_audit_v3.sh
3f573cc8c6adfb54c949830ff1e2e4f9cbbc28257165e25930506831b940da2d  openroot/bin/gh_audit_v3_patched.sh
f349bb71bea2518c9ebd33333cb34c0f4f635dea6d53e77409962463445418ba  openroot/bin/gh_hygiene_apply_v1.py
eb03e4166213cedcb434ebe3bb655a2ea49b03a6c7163e86587764f0cb280c48  openroot/bin/git_push_delete_v9_20260920.py
9a036d96e0d1adaf66fa7e23e4528f35c027424213460df8f04fb2d397494813  openroot/bin/hygiene_fix_driver_v3.sh
bbf00977d9e8ed2c7bdadcba0726751950fa36f5eefc088c7cb9855180bd5520  openroot/bin/hype_gate.sh
8485978c01c64753c3c4a3d7401eac7e4e84042f5179c8b6e879ca6fc8dee335  openroot/bin/knowledge_probe_v1.py
2c0116e744979947773c535132515ae6ea16f7b7789c3b03ef1285102964b48b  openroot/bin/knowledge_weave.sh
c52fb68890436352ece13257350342b5d7601f30c411fe74614e6e0774f9a975  openroot/bin/large_file_cleanup.py
72ddfc54812932ac5d28eec3fb4901cfc770c083ea7c3fe737f7ae4e9fefedad  openroot/bin/lb.sh
31361f1eeac1af38871ebd8590db6a46d30d1c2b314f4bd52d87a08bd6290adc  openroot/bin/lessons_v1.sh
0a9f5417ce6b8e69960e634e7c4b968a7bd110d519e9ed86b054ce8acecfa1f1  openroot/bin/license_fleet_continue_v1.py
36a077ac8f76df702716d9e530cc446d6dd1adfe25d7ddadb433353523e1a9dc  openroot/bin/llm_rag_integration.py
a33243d1ed8aa20217764ee70946153386eeca47ea275d5bf637435f9356e500  openroot/bin/lumo_lib.py
cf868172043c351e48f8ce5ddb38bd298230d462e129c46272f3e60a8ad78f71  openroot/bin/master_finalize_v1.sh
0f65792a648c704b057743ffd1d7bf15ee5766b72e9ed697676b17f5aac331d8  openroot/bin/master_finalize_v2.sh
74394ca265b62776dc38c9e73566ee5b465e0cff9f70755a089683e3c1d95a21  openroot/bin/master_finalize_v3.sh
9ad2e76bf445219a17028c68b5a6ab96c37a6963288518dd1d83ce3073c5fe2b  openroot/bin/master_harvest_v3_20260920.py
c30d6888bc4d37075e73d07ddc4b42a24bf6d3d0a628fa52305f5d606b09b1b0  openroot/bin/master_purge_v7_20260920.py
d4a3206bccaedeb148349bf0ab2ef2353fc21d021af431e68bdb581e4b57bb95  openroot/bin/master_salvage_v1.sh
f0cead111ca82c63a15af4eea7911af02a382fe2ecb10adc3cef4346c69c6a74  openroot/bin/master_truth_v10_20260920.py
cda9193341128243bd2eefb854922b0d15819310b9883fc1e38c1faa8066d920  openroot/bin/merge_pr59_v1.sh
97c932be53c7309fe0a9d335cbca90ec50909806be54b331b2fdc67fd203962c  openroot/bin/merge_pr59_v2.sh
72b5f90fbdb1b6345fea0c78410374528c97e2c401c24dc897f4aa9eb26ebce3  openroot/bin/merge_pr59_v3.sh
f40c8cea7a3a552aabaf06b5b05c73630f5a4a7550f4873837c1ee80f35731d4  openroot/bin/mesh_fix_v3.sh
945e4ecfeadde567776c71be6b2cddab1757b1143414354a015814e874c8bc53  openroot/bin/mesh_publish_v2.sh
d302af1c6dcf1e3d23f7545458cf165a37bfaa1def0294ddd3029ea81d12b9e3  openroot/bin/mesh_recruit_v1.sh
13dde54aa3d8b8de2aa6b99b1ee737312c4c565aa1f5b6483a1fab4c658cdf8a  openroot/bin/mesh_refine_v1.sh
8d5567aa9f8ae4aa5d882f93c0714620a547227fa7c7aaed8457d9c4b5f6bab8  openroot/bin/mesh_retry_v1.sh
e319af444baded4dec3bf0343963010053a63e77c7e4b381aff57e13e755a2d3  openroot/bin/mesh_ship_v2.sh
cec7080a86233b246fe8c6e21cabdcc3d2bd89b150eebd6ad6f65243c67d9a38  openroot/bin/model_prune.sh
cc2e415b25c80915b922a98b519f800579bb2b425525ea5843b9cb1163ffc2c7  openroot/bin/model_symposium.py
6f54af0d495914ce07158cc64c570a5164ba1899b8af5cab5d9e7317f8b6b0f5  openroot/bin/next_actions_20260920_v1.sh
806ccbebed8582ba36281ea43b9b31bbbd56848fe9bdfd77c6c16a968af2ff90  openroot/bin/next_actions_v2_20260920.py
25265b898be499794b55753e497083d3b49ef31631e1fc070d0561894961ba8c  openroot/bin/ollama_diagnose.sh
cf71c35f35f022f4ecd0d840425aa4472a688e5b7d4dd5eef020670a1640f608  openroot/bin/openroot_mcp_v1.py
da03a6c9d7bb97979ac93dc193b2330779d13f9b18c2dfead96c9eff6563a370  openroot/bin/pr59_reopen_squash_v2.py
7844f623fe14c6c87f4a6715ec95c58174daa90a054ae8a60e17c200f597c430  openroot/bin/pr_intake.sh
f011eab9908db36f3711c918ca2816f7e598c10dcf624239cee8e2a24c41f321  openroot/bin/profile_update_v1.sh
0138c44f302f100132ab987a40742a9fa9e2de59f1c2f2061a78263e56c7a35a  openroot/bin/queue_advance_v1.py
5c2aff0229b5c5fab3f9b4cc90e4ed4abfc8c166a406ad75db5ca0a90345ccbe  openroot/bin/queue_directive.py
9cc62375c2393724f1643df963663745169ec26c5c1455495a29538639eaab5f  openroot/bin/readme_contributors.sh
09fc9cede512ad148b49d76be859e468e3f1f347cdf0b9fa0cf57cca37578fa0  openroot/bin/recover_v1.sh
72e6cb1cd3fa722fa0da33160acfb9996f8a6bf0141c853a9b42e7cb470bb134  openroot/bin/0000_agape_one.py
2b74cbb2f68d0037112cd1a9de20f8323314bf46370779ee23c33caa71c7a127  openroot/bin/refinement_loop_v2.sh
b35475bc5e7c502dded0578ca23d9d8b15361bcfaa33b91c2d95479cee7ed88a  openroot/bin/refinement_loop_v3.sh
f4ad485787a31e50f7a24903cab681d8e30e3d3bef8580050699c82324fa10a0  openroot/bin/repo_clean_v1.sh
500b9dd221485462ac3a89520ccf6e882daa2ff28c56dc01a3605534529da861  openroot/bin/research_ready_v1.sh
21738c67f56c6852bf7318b1e9b6f57a70bda6397f853d9e98e4e2248c0e1c61  openroot/bin/resolve_pr58_final.py
97010e13039afacf403cbc490af09bb9c9c6ab221f26d49291648fb3b5148001  openroot/bin/resolve_pr58_v1.sh
4f0531b467811c09e5e006263f0f0350b1a48ddf766b09a5d1f97b80cc7136d7  openroot/bin/restore_readme_profile_landing_v1.py
8dc84c8187827bfbe9736c8e0ce79aba475d5b9d9b02c0703d628d178de1c0d5  openroot/bin/run_handoff_v1.sh
26f6ac2a4349ab374264714e0694792e2a7903cdcff1ee9d4c93db2c5bb3d015  openroot/bin/seal_session_v1.sh
7b2cf8d7ca856252484cef63f31b15a1a0c0603e5cb4d7082fba2168c365b238  openroot/bin/secure_and_commit_v4_20260920.py
34a6181a8bea4012595dcba2ff96cdc435c4bb155a8208e98f770ff3d971c9a4  openroot/bin/secure_and_commit_v5_20260920.py
b1ec8d115655d76a3d5b2ff10560b6e808ebe3e2f938124ffe80e4e60e6de7a7  openroot/bin/session_seal_v2.py
db00eb72cf76e2d8fcd72ce1aac607458441b43fe2e962f62ddd029f88211096  openroot/bin/sqlite_params.py
e190d11cca20f731e21822f7b5af548459f9811999c769de52541eb31e82f799  openroot/bin/task_recall.sh
a6ac9fbf8a06710045da7e29eb3d4a1174053760c338f3cbdf1730ee373541ae  openroot/bin/unified_workflow_v1.py
6d5ea437dd7ee3f122642eebb86b038893dfd9296db153341c466f2f5a6a7e0b  openroot/bin/universal_index_pipeline.py
8c73d6e25786dc20bc9fedc4b8d408b74ff3ed7cdd2ebc1ad5f8807806e661ea  openroot/bin/universal_unpack.py
d38d3663f40679840636d4d9c9587418c031d5b3d70ca524d3ccc23ab624af08  openroot/bin/weekly_audit_v1.sh
4210dd16b0b2495c258174a9fbbf082ec4445f1b0d0d5e16991ab7f5a9e6da47  openroot/bin/write_context_bridge.sh
18723516f1bca522c938278eb62441389f371c7b085ae651e73b07e8ba0cd216  openroot/bin/zd_census.py
7292fc483697e82c93dfbb8c1ace053322f6930a0f820cfb93e2d9f3d6301d76  openroot/bin/zombie_ref_kill_v8_20260920.py
c8d223872a93d1cbdb882c8c9f850d151f23140ea7fe5e39b49fa269f16a346d  openroot/bin/init_knowledge_db.py
f37dcfbd8eeabeeb6d5ce0197edf7063d8a63cc2c6cc675f7f92a949856d3455  openroot/bin/doc_compile.py
4b41ead96db0b83fa2fbc5b4de9e731786d1c6495252a486f64f02cc01e13724  openroot/bin/agent.sh
d20f8b65aa75d3bb2260bb1996a64b04db3334f3ea5ccb1df109563a28a70676  openroot/bin/aider_task_runner.py
baf171319e735d26968a71779429ca9b0d27051c9abd40dec9fa71fa28ff99bf  openroot/bin/env_map.py
1dd97e00a66fe534ae0d50eb621db22a03c0348956a3771dd56c27ce3be3033f  openroot/bin/finalize_workflow.sh
adfb3096460bf877f4610f15c34efc71629dd79f7ae978ddc6bd84d7c21fa9f6  openroot/bin/light_cone_router.py
9d318ef1d30fdf8a90b13c806ce7c24694273eb23f26871b17f420eb4361e7ad  openroot/bin/rebuild_core_workflow.sh
758d88930be6c026be236ba98feb0d26739c841f1625ffcc315e7fa550581832  openroot/bin/0001_bridge.py
d6303f2256a3174a0532d51685393226427bb52893167d81109ea1e1199b48f3  openroot/bin/0016_openroot.py
c42f552909d4c4577166fafed14494f4382f37ee305622652c4fa8904a0ab4eb  openroot/bin/refine_next.sh
69cec1a0cf11418b01bdd992112f5e6992f2eb12f6411cf83cc01e4b75cbdbb1  openroot/bin/tier_dispatch_v1.py
90ffc9384bf663d5e71d441f30dc7288aa95935454eceda889fb20e7651ad070  openroot/bin/config_tiers.py
f0e11bc0e60fefde49643f76c5dc188a6b32d1deaa962fabba1af4a21e1ba48d  openroot/bin/contribution_tier_v1.py
795872dcf974050703728d217175fb20e5bd811a05c113cf6be602d1d8ec4fa4  openroot/bin/lb_stack_gate_all.sh
bdaf3fcb69b59093dabb1fa8f4b34f4f2cbfa6952515af8b679d2b1e7d2a01d3  openroot/bin/multi_router.py
1cec34203bab25d7381484408081a862f858b17532ae405708636d3e37fb7855  openroot/bin/hive_nursery.py
8b9041cd2b5024f18a7a70dce870b8d585ce1ca818f4f71f8fa7572f43f5ebfa  openroot/bin/window_extract_v1.py
df2f037a6044eaa52ec78815b26134197622bb85dd4fe162ed902a309d7d2756  openroot/bin/agape_cascade_v2.py
1461ac2ad7c93066443e798e3595cb9f9cb1084102133d9af75da84237ed3470  openroot/bin/agape_cascade_v21.py
5adb8583d259200c04378ef33217b4be0533c7778bc76073fdfe2bb4e82aa881  openroot/bin/agape_cascade_v22.py
79ccc78d656ddbdd2d39690b807cdae8810c7636b8b5b77c12791a0c025a5de7  openroot/bin/agape_cascade_v23.py
040d7c6d26cb0c0a16b5a7d56d55fac25f72cbb371bc914db4be8f081f072632  openroot/bin/agape_cascade_v24.py
5407fb78d1298d897c667e8b499add3694a789f505a90a9ba88160c7097a9665  openroot/bin/fuse_router_lb_seal_v1.sh
fcfb6c0fdec19bcb6f60169560eb44045cd316db4399e23f9c4c885f7ba9e5c3  openroot/bin/keyword_router_v1.py
ffd54eb137ee770601db18a7418188ea34548178038e300c26089a1837329882  openroot/bin/lesson_stage_v1.py
d280cba3e15c70bc78aac74a65cdd06759dc2cd713c824b8231fe0e596c0eaa9  openroot/bin/lumo_bridge_bot_v1.py
d56bf5cea47b486b1dd4c7aa192df6fe7a6e2a25aa1e47bffdf2ff3206d691c4  openroot/bin/superlinear.sh
28d691277ab0227f39c89d70c280cc180cc534d836b37e9d9f53a790330b67d6  openroot/bin/window_cadence_v1.sh
26e8a07be6a23dacf15be2d3aee913b81ae60b0f5b2951bbce2b283586822297  openroot/bin/agape_cascade_v28.py
04a952a62e1e7fe645295777e2e42e57e4ecb6ee9aac0ea20570c6af34ef8df6  openroot/bin/cascade_release_v2.sh
580b07aa739550b0e08e74014ddddfd99b5bbd9954309a27d134620b8c48ebde  openroot/bin/0003_agape_clean.py
356b4b21977513a1a67126d2f3fd6124d950aacae32d1cf6eaf019661f9652ab  openroot/bin/0004_une_client.py
97be438750b12233ab85bc02e01035151e3b0a3520f0a2ba1d938dc0cbe2da47  openroot/bin/0006_agape_slim.py
4b7a677436a63aa092f6ab44b3fce0da94f39fc008ca3327cdc236c430b23973  openroot/bin/0008_raise_to_6n6.py
f4c5668618dd724e5bec01f7e79050c7f697f6960059049ac026ff429ab817bb  openroot/bin/0010_groq_fallback.py
0cd3a6176896cf7c009240268d71d9256e713141d5e0f5264f29aae5635cfd94  openroot/bin/0012_newton_chain.py
c41aea80e79e9f05e731276d5b823ce94773301408d918bbe3cfea92bb355f11  openroot/bin/0013_local_rag_search.py
80bdef56a6cae1efbcffec9813516f63e05098e3045793a85be66df4f8407541  openroot/bin/0014_agape_hierarchical_raising.py
1ceaf592f02be2a0b3fc4320e526ccfaee951c2f3b651b1544300b78d9063024  openroot/bin/0017_mdpipe.py
1fa5e746d67c9d14efd5c55b8030f95fe30d53d34cdb259b84a0716f4307f7f5  openroot/bin/0018_test_phone_tasks.py
a34f0d53c536ea6ef56826bb50203543b836e960ce811a86bf0f43a0b0a8c162  openroot/bin/0019_enhance_tasks_with_efficiency.py
894505648c39c9166e59fb3e91cc2800c7c1968f1c1e09577ca2c9e9db2a382a  openroot/bin/0021_fs_hook_patch.py
9a63d9c013a3d06a34dc20c8670c28de867d6e49fc94d9a804afc119cd4c339f  openroot/bin/0022_agape_init.py
6f3629a6dd6b74b61c41b5b286e67bf8293e80093314eb07687fadbd1d5dc649  openroot/bin/0025_fix_chain_verify.py
971f6d638bdf99314515acc3f686acdfb249172fb0d87f54208c1e6a005290d9  openroot/bin/0026_openroot_hub.py
bc1234dfe2c73080681886d2f12d6648aa1f2af9356c2cbf78ae1dade8c7cf4a  openroot/bin/0027_agape_frequency.py
c2bccfd9e316e5a1526ad7c08267e290eecfdf00ad5df7fbdc6f26b08e3daacd  openroot/bin/0028_agape_neurogenic_kernel.py
a36fce85f9dc35024a5221c88163eff4b7b0a4a3d6741aaa58cf59285dc03a9d  openroot/bin/0029_agape_evolution_v2.py
77667a63c4f6f743b902958329644a60ad4c4d24334b1b809e83e53aac7d1c67  openroot/bin/0031_unified_agape_engine.py
b18250dacd94dd2ed1184e042f4eca5d549ec7080394a5dbc0dc16db147f301e  openroot/bin/0034_repair_all_une_and_commit.py
e2f1963a7b58efcf8fcf75689b7a2b213ccd06b19dac7f1dbfcd05bd047f780a  openroot/bin/0037_fix_last_une_error.py
803aa501638aa1733ed3cb44719e4ea58429413211c75d47bbe9501edce37b53  openroot/bin/0038_hive_swarm.py
871e0b0f69fb16ed327b7757f595b9f0963367e8dee65a954af4f9cfa19eb755  openroot/bin/0043_master_codebase_orchestrator.py
abdd87ab69226068a64eca2e558d4f6f29f15fa1292a8168fdd43e437f2eae05  openroot/bin/0044_v7.py
30d0c1a8cda7b594e97e2f44d5aab84a6e89164ff43be50ed9e027225c9bd261  openroot/bin/0047_joule_leverage_analyzer.py
7a4b6fffb5daf37595245d446223edea80b07dbd2f8ce53ff35b7b3f5acadd7f  openroot/bin/0049_patch_voice.py
39b6b32c60f144b1f3bc7f0da71e30c51344d0345c97ab771b7849ebbff2152e  openroot/bin/0052_une_atomic_library.py
0070c19cfb50608838864e9dec62a4e6634740f1bc51e09e8686afe0e3f2dbb7  openroot/bin/0057_agape_primitive_forge.py
f15c10dda22e30f267e225768e07b05d6ad6e2e7dbace67ea73276d222096b85  openroot/bin/0060_emergency_syntax_fix.py
0f954dc6f30d6b3ac1230cb276ec32271069c70a78ba0e84ba31219ac6fbe644  openroot/bin/0061_diagnose_and_fix.py
009e74507c85695b8b068853efbc8b96b61b186d4dbc26a340b709dcdde7ca6f  openroot/bin/0062_diag_fix.py
2de1ed86e6006da242b87221b8230b57dca58558bbd3ce3c3c8b45b5f1e882b8  openroot/bin/0064_fix_final.py
36ddfe7c5bb34941cebf24d8522d9d1321c233ddfc2d852d054960e951ea41ed  openroot/bin/0066_storage_daemon.py
67b05a3c3c94dad5b22ac969624a9885df700e752dad075f2a6f1e34f564afe4  openroot/bin/0067_fast_backup_daemon.py
3716cadbe304d415aa8c830e2ada43ce03c29a94b84bc9c6c37af0a2c8456b51  openroot/bin/0068_agape_net_setup.py
ac42da68fa8d315d42ca570720c64c83948b0357dfd20f5878018f21c67be154  openroot/bin/0069_agape_net_full_integration.py
42ca14270b8471ed9dc8645802603c93bdb308531337c45f85d9e9afe56c29a0  openroot/bin/0070_index_content_blobs.py
0ad0e4d40e08f8a2e6032f049dd08412111058bd0f06ca6b1c3e52c0b82128c1  openroot/bin/0071_une_fix.py
1ce4e39207461e6be95237a393e4839dd618661b3f94c49f99fa7df52eb12262  openroot/bin/0074_hive_entry.py
a4e89db9891823d3b3aa0c0d127d8af4abecb4e980584bdb62b668c37ada7b95  openroot/bin/0075_structure_enforcer.py
4738818f96529746e2d2251c1facff9d98c88b5ad1f49b49407eff29102350d7  openroot/bin/0076_immortal_context.py
c3aaa874f63a5b774eb0c5b4c44cb2f843874ea68d19825c52eb2b1925463a16  openroot/bin/0079_bridge.py
ab07da7a346f38afab465081115dbe38e805783b3fb8ca4989fa645f6ccda473  openroot/bin/0080_une_master.py
6aa29ef9a47f5882d7bd5b17309cdcf141b818af3587a14febeac8b281aac9bf  openroot/bin/0082_autoupdate_loop.py
ea0f94f86eb8cad7785fe397a78b71e1817e02d41cf81d6c602fa5543bfd8fbd  openroot/bin/0083_cb_user_hunter.py
ef1503f6248974a2c8d975cfcff17630d87d429a054ff1af68360aa4f8093ab1  openroot/bin/0085_rmh.py
d692ce5e7f87181a34a95a29b70fc22eb66d3d9b33b612365f53b9e2f5fc04bb  openroot/bin/0086_groq_max_cycles.py
478336f02d1c3e408867dcd29d5a6c7637c55b043a19cbfff3eb4453c853dd23  openroot/bin/0090_une_atomic_library.py
c8bc1b16962df68de7ede14ef24c1c50039d1f0a93289aa52b65d1a4b84fa612  openroot/bin/0091_justice_module.py
e5ba29cb1e2f21c46e3514992908d04e715eede224cfd7cfc0e1cb966861a7c5  openroot/bin/0095_deploy_thermal_loop.py
fde9f8a893ce89fd00b5a5f6d4d055f76bf96abf6f821a84f873c7c29a9d95da  openroot/bin/0100_find_dupes.py
a3a15c722b25c48c4884b33f50847ec361989c8208584982b71a8ab48337f0bc  openroot/bin/0101_setup.py
107793e1fad64ce08ba6e79eb2b06736abb6e43f3130fd06a6fbe917e95dae05  openroot/bin/0102_esp32_btbufs.py
49c8caeb00495b6bd4e9603a7473f83ca1ea3c445797b4257e93926b75b9cda5  openroot/bin/0104_organize_docs_a15.py
fffbbdff75842385c2da84aface8bb0635ead7686648e9a884afcf590533ab1a  openroot/bin/0105_organize_docs_a15_v2.py
3f2508cc771fe6f87cfff765c57752155e08ddf91f63217af92a7e13bc0ee443  openroot/bin/0109_coordination.py
3d10cc3cf4e2fd6b5693401e0c720e4d0316e3e93c40cc3373c9805233612d29  openroot/bin/0110_eta.py
5c004af613997546bc64c134d93e1f758c07067d40a17788468207c2fefbe7fa  openroot/bin/0111_next_joule.py
429f70830f80ff1a6ad4d5ff62dd2755e23969f5c90514500c07a27252cef8d2  openroot/bin/0112_postulates.py
ebce54413d07eda228f98d98395989d1bb0997339ac8e1472f423aa685cb9044  openroot/bin/0114_synergy.py
cb13b79b788de46b5da51791db068be7728af90a8aae88c1c460d900f52483f0  openroot/bin/0117_build_as_lib.py
9a5b0a84da4980d2c8594ae70a4d15a0637cc570a0addcb2c676aa9f825841b1  openroot/bin/0119_merge-bin.py
0facab3bf32b5ca94644aae07902cde6353439a7fe3b70778b042cb3a8a3657a  openroot/bin/0120_test_thermo_optimizer.py
a201e4a4942d3a3a937b1ecb318d4467f43dbaeec8db5cc2cab599b353d5cc57  openroot/bin/0122_build_hex.py
6058c1fc3ae600977eaf8854785fdf0f2a596172c4b1dd08e03571a4300ecade  openroot/bin/0125_base64_to_hex.py
bf3e747ec8d44cff7885e34d5d22c9352f861ea1f819c83cd9bf572266e7cfd7  openroot/bin/0133_generate_ci_matrix.py
8f6c4c4857b4134a0b414fdd38f757d7c166dc5c9ea2ad0d86587315387e70ae  openroot/bin/0135_genpartitions.py
5e8c80686d2bd485b2e3d8d5e3bfaa2880aa7aec8266b2e602ae2bb128a0c9db  openroot/bin/0136_platformio-custom.py
47f7a781d17713c9229686b1e704b60312002e306cc10f5e971aa75b2892c505  openroot/bin/0142_uf2conv.py
99c9b55705f2f70a9e447b844c02020b9e34d45952b7648270691aa9fba5d4a9  openroot/bin/0144_add_mbedtls_sources.py
fe867f079bb1bdca0f848655e52eb3271abc080ad786917fc8a6be64cab49b10  openroot/bin/0145_lockdown_provision.py
2182ff5317fb119de69491fc3f8d9cb919f51ad701afadf0db62886bb5e56575  openroot/bin/0149_core.py
d95ebac9415538b8042ed33809ec799c1d2f9ee16db8ecf57af057aa6040df4b  openroot/bin/0150___init__.py
ace651b6b5e30c1cd8db89e26b14e777d6471d62fb07411ac1574ba09de723a7  openroot/bin/0153___main__.py
ef6d0cb7a874ed471ee76bfcd04385fff2586aea0bc3d6fb3dfb3fe41f758ac8  openroot/bin/0154___pip-runner__.py
5b1c304b063f066e90cc381fdf606cba31323bc76045e75e802a606d47c3bccf  openroot/bin/0158_configuration.py
d5c1ea8ec7c50ab3057f7079b70ce87314c951d1cc2e85d4a72e6526816a522f  openroot/bin/0160_main.py
caf1142d2b59b6dcbd2a9969f3db438acde119dc8a43ed8151b14b989ff98a79  openroot/bin/0163_wheel_builder.py
5b3bac3d319620c790416495274876ada7c69154daf56289d874fedbe12866b5  openroot/bin/0164___init__.py
397c2fec59f60309ca3626a12479e3b6f68a2e776f54bbfffb33be96d955f6a2  openroot/bin/0168_cache.py
0e1c42feb4a4f9b78a75bb1885fbc1503a2f4075fdaf78071ff8cff7eabf98a9  openroot/bin/0170_filewrapper.py
1d0776225950d391f33e454b3174c5dae5f99a31108c3064c42a94254383a599  openroot/bin/0172_serialize.py
86c19cee0f101904d3fb87fcb60cf700ce6ac12720e853b405274b491744be95  openroot/bin/0173_wrapper.py
0dea37ba8f7c694c887dd28936aa1f7921055b00f3ad5d907862d72ec82ad008  openroot/bin/0177___init__.py
da34528d1238a3ebe55de4cad8108621486473a7bd646852b1a711339a2c793c  openroot/bin/0178_compat.py
42fa7be84f49737220c98b9b9e9a88f5f4bb7ac78639ee058e97952aa2adf48c  openroot/bin/0180_scripts.py
bcc3c6bec4b88fd845e98f64dd3ca89b569a1cb6f4ac5999004cb378075e97dc  openroot/bin/0181_util.py
30fa8d0cb65b5ea19a35d5f1005862a853ca1105e3bb68cd42109ecbafb97893  openroot/bin/0182___init__.py
33648658dedcb3fe81df6426293c9337ac50199798420436c225f7fc347a9681  openroot/bin/0183_codec.py
1fd277e55903d05f4bf6628eaa378d19dd80f956ba1653e8cfa273e0aee1fa9b  openroot/bin/0189_uts46data.py
7424d67a2f1da64accb100dc8d093be004e5f47b08047d326edf3338f36a3187  openroot/bin/0191_exceptions.py
fac2a4a6d62acd8c36fb1dd007225ae66078adf3d6bb5a719191d1c755801426  openroot/bin/0195__elffile.py
1dfea707470eadac84b3debea77a085c08069c5aaebf6d033b997ea36fd79efd  openroot/bin/0196__manylinux.py
29fda7b03c38739e17f36a58f1b6b8174d81bdee8eca018c0232fe05e82a71ec  openroot/bin/0198__parser.py
eb48d16c5efca7ccf930a9cd77a700a6b80e69d0891d5d03966526441a8565cb  openroot/bin/0199__structures.py
5d92005452bdb871b84421a9ae6267dd522751631eb3185afe4cad26e30ef5e6  openroot/bin/0201_dependency_groups.py
038978cbfd124487b122934b816b5ebc30c83886c44e1a6f5a6d5c3693315482  openroot/bin/team_gate_v2.sh
2d0a8d2e80e454c8f307d5066365658372bb40c46aa3fb31342907c3bf063691  openroot/bin/terminal_log_rag.py
d56130d33b4e32a5f0180546b4c333a0a334e0baec0bd3e4d607e2bca4c943b8  openroot/bin/bot_stop.sh
3a5bd0e8191b5671f9606604c8a36d4edce7837261f9294f5a549d8721a9ceda  openroot/bin/markor_compiler.py
f69d9b127bb8d5fd187cc1db9b33a84217125910356051f19911af7fc12c7c22  openroot/bin/compound_orchestrate.sh
e4ed5ef17344ee9ddd814d3f183d8cea5078efe71dcec74bfeea47bc5865e14a  openroot/bin/openrouter_client_v1.py
ca0e79d12d57d50fe1355ebecb75ccca3ca390af2723c89bf5750f3202fce87d  openroot/bin/contribution_tier_v2.py
ca292c2021c229e90ed9060f71c99fa58ddd247e7d468f456955117636b96301  openroot/bin/lb_loop_v2.py
1923c58b310fd64c94f4ec5303ceb301cc98472d3a5c9fcca9bd49e71101f8d5  openroot/bin/lb_stack_sweep.sh
0c2e2ec6d021c881e38494e68f1c9d8ba5f765a6477d8e61ccd1d8a4327abe0f  openroot/bin/lb_team_gate_call.sh
905efa24b7a1e8e5c63f9194c2a341e38ee5ae969725d4ae12f01fc3dbf857ac  openroot/bin/agape_cascade_v25.py
486cbec2895d1f61b455cf025e7a1596844adaf343046e06856a98451da7ee1b  openroot/bin/agape_cascade_v27.py
a03d360e5151d4cbabbe578fd3a73eadd45a1ae054f2847415a8f7fd1f6cddb3  openroot/bin/0002_groq_max_cycles.py
8e34abbf799b7c3c3d3ff8f1e05a1de3f7a6000b68ff597b4a413bff6b040302  openroot/bin/lesson_ingest.py
d086a441b1593862a80879d5961c3d1a1b6ccd6bc651c9659c213399fea30f37  openroot/bin/lumo_bridge_run.sh
928be079cfa988e5b2bd47e49d6da500b3349a34fe166dfab221396915088803  openroot/bin/popw_ledger.py
e7c1c85440b50d33b6be7343e2a93b14e9202bc853bc6e73e7a9115d033a6578  openroot/bin/qa_fts5.py
dc30d7fd33c4a15cd3da828b5c7b0215bf5063956ef551fd2c1c85496c035230  openroot/bin/readme_draft_loop.sh
8c1c454de792ae241e67cd19f5559a7d9357009321bc57e24e5e1d20ba4e5837  openroot/bin/window_fuse_v1.py
c144cde863647d337ff1b52812d5497194e3a7d1d73421918ab845c99c81b2ff  openroot/bin/agape_cascade_v26.py
1acbd0957a85c2cdec20c74409ffd0e18726b77878ab717b49d8e6d9c216df62  openroot/bin/key_setup_fuse_v2.sh
79d6c8772f4ca20c4f7def075d23638eed0943e69189027f3465a6453c7ad0bc  openroot/bin/lb_commit_seal_v2.sh
ade0da42e6aca3bad7a912c5965266291576ab2bbb4b7b3b2605428ec12c086b  openroot/bin/0005_test_une_full.py
ab698bb8da909a89f2a056e9b0f96f1e4ea40ab65842f085bdef9efb33792175  openroot/bin/0007_faiss_search.py
dad4ae35e934de9bddda1c95ac4a4d96cb054f3e16679418a80aa164cdabd974  openroot/bin/0009_batch_nomic_embed.py
81533c8e3eed23f6d9b4c4d5bd52a14f62127dda6a472c2e60eea937daf114cd  openroot/bin/0011_one_principle_n_power_n.py
2a010a070181c1ad22b6ffe990721853d6def385b348e26ea66b53d119e1a012  openroot/bin/route_yield.py
89db87f53665bdebfd8595bf424e0cb349d4cbd285e9a314d6597bde268a23bb  openroot/bin/0020_apply_fs_hook.py
9b67c65247fa651e21d299d08ee2cc475b7ef95b3e4f7fade696cb7cbf964ea8  openroot/bin/0023_constitutive_voice_engine.py
9642f2a93c46cd9c7e562a4411cfae51fd27bb0acb40e6c7a0d64ad7a39269b4  openroot/bin/0024_constitutive_compiler.py
6e518f904159575e4787a29a68ef6bbc8d13ab3b952623978687b4ea792e1eb4  openroot/bin/0033_repair_une_syntax.py
5171887db6ebb8da5909fff2261ad03ea61a1210fad6c3785ed296baac94a539  openroot/bin/0035_compressor_node.py
37921a8779cd1c963572fbd17ab75782ca999ea96bd274e25b67d53c021d4327  openroot/bin/0036_core_engine.py
6fbcd043a3951016242f9faf20273d853a37cbfcac1922cd0e1fc22296abc867  openroot/bin/0039_apape_net_setup.py
a848c74f05700c7f0b7355d8ca91aa6c8143569136fc902e4c5048813f2a9cdd  openroot/bin/0040_map_files.py
fbfb274e8fdee0e092f3d5b633dae8bcd91231b3f5c1c1728dc3ef9dda98df51  openroot/bin/0041_inspect_map.py
08cf6f8ee69e0e5165508c54092aacea13d621325c751542fe01d16e689fb163  openroot/bin/0042_build_coder_environment.py
5f243b0c65c9797d847adf2c37dee9a6f21a8ac8fb1035669775b3e6fb5c9385  openroot/bin/0045_swarm_bench.py
a9741944411f24bedb89bd3bcbaa5311ceb57cf23dad88946f0977a1bbd20d07  openroot/bin/0046_smoke_fix.py
e7f32e365721f5c4c1c8337f87cf59e5ca86f4836bedaeb75a3915eeea245040  openroot/bin/0048_snapshot_bootstrap.py
d871e9c40bf9c9ce3c469182b806e3d018919fc127ef5bf26bccd37337a2197c  openroot/bin/0050_agape_farm_os.py
88ce4853e5e3a9e0097f9e42c46c22c727f83ef6899486def4be4e528210bcbe  openroot/bin/0051_une_max_efficiency_lang.py
c54cd37678a16457d4d5b342537c52c95f5575fb75a557bf7ced61519acf6d75  openroot/bin/0053_agape_kernel_v2.py
e169e8f6f177d8627ee44d141402aa121e47ffed34611bde5880874a32299271  openroot/bin/0054_agape_ledger_chain.py
77f7fa9d5756f196b0fa28ecf0ae66c0e859a951ff0041dad8a7d46f94908314  openroot/bin/0055_und_protocol.py
fdc87757b7da44b0f1de597b558227630615b203de220f14ab9cb702122b16b1  openroot/bin/0056_agape_node_bootstrap.py
67d32e91f45d165ac5cb2bc1a5b153aaf9b353b8251dd4112cb2aa01fd028ef9  openroot/bin/0058_run_7b_coder.py
d0084794a9dd43d675c5c63054272a3fbc11ae2a1acfbf8031dc6ddc4def784b  openroot/bin/0059_final_une_syntax_pass.py
7796f195362ef873813b90835110159fafcd51fb2f36038336e70e23f7418f62  openroot/bin/0063_surgical_fix.py
307eb605bb8dde8de6f94b4e8f9b576a3a1e2c23a4f53fd7290608182efa5504  openroot/bin/0065_agapenet_unified_setup.py
3efc4aba22445812291dbff1f23ccf8418f09a6c2582d844030351f093509e7d  openroot/bin/0072_deepdive.py
fde2bc69c98a14542e4d61ea13905a6d544c4572ae0b9a6f4e0c6348555d3778  openroot/bin/0073_audit_repo.py
a851b4b70c2541ef33cd407d8f478f67cc53ea91d65867d3167b782f900471e8  openroot/bin/0077_aggressive_dedup.py
b844ed72762552f34d20cf96ef41027ef3a0088e7da85d8be50362cad733db3a  openroot/bin/0078_openroot-inventory.py
9d93e0b481442ae23c07e9c8eab18d08b971bde6e0080592e0a863d8ca7c794d  openroot/bin/0081_governor.py
a09daa00b3055d83b1437387abb5ed285be5deadeb1e871dadfe12759466edeb  openroot/bin/0097_search.py
949d945109bc8821139d21287f7d465611439849c6cc8a331dbfadd21fa9186d  openroot/bin/0084_dorks-eye.py
2708182446d0b88938f387bcc8c6606e216fb840c02ca442f388d33f5939ddd3  openroot/bin/0087_agape_synergetic_calculus.py
199bc3b9cc02caf494a7f6a8774e39749198ec74118e37967c87612821841ec1  openroot/bin/0088_CREWAI_EXAMPLE.py
a1593af63e3992a6885fcc5a91af5ed19a827e1c3b9ca8126439b81829cddced  openroot/bin/0089_agapenet_cosmos_engine.py
3969cf8afa73561cf3f9bd1aa54d0477a70f0ec804933382a739673dff847c77  openroot/bin/0092_laser_sim.py
bfeb15c499882b3684f216d792c537212623801f500f3e5ff04ee85d2a920600  openroot/bin/0093_deploy_openroot_kernel.py
17278e908f496e723dd8c41920dd7796edb8c762c41e7f77fe83d45c512f7be7  openroot/bin/0094_deploy_v101.py
5d4c8fc4c5c16de107cefbe5ba2031d48bfac94c0da6373505fdcb8634744606  openroot/bin/0096_deploy_v103_evap.py
e596b1e485ad6d572ee96ffe0946783ea060e2ae8b6071899515df4d743bbc28  openroot/bin/0098_local_scan.py
ac920c9ab37fc4f0c4feb0e930fc5bb8f4461e412b7fea383094a569cbc5a0fc  openroot/bin/0099_scan_all.py
19154a6763af631362df08397928158de510173f6fa55fbdcf09579659e420b0  openroot/bin/0103_release_hashes.py
0054de81c9c9c34bb2cdf79777badac915bfa2567ea0bca1a8fe87978ec2a51e  openroot/bin/0106_init.py
0d6f04d6d890942e1807452dbbc8a3e763f8aacb7e041f17e183d5bd1143b6c4  openroot/bin/0107_agape_mesh_oracle.py
6ca7b3030fe6d1a8a55fe29371cffed47bd5b48c4a0d8f0c71829975b1d0a4a4  openroot/bin/0108_sync_bridge.py
cedd4871e20b1ad8ff8458450883bcbce3ca4e29d169bb4763f2fd251170f44b  openroot/bin/0113_selftest.py
e5ab4ac5a22ebd99f08ab66c6b702e28839de9bcf0d680a06e104311779808f3  openroot/bin/0115_thermal_loop.py
b7f8c74e4e10d0890b2e74d74babc0277b268ec6db0708e9357fa652cf960c5b  openroot/bin/0116_git_rev_macro.py
a728f1b0080f9ce8c20737238cd4b566cbfb7fecf9cc50bc39a04756e98de045  openroot/bin/0118_create-uf2.py
435c47342c67a0e9a5c93677fb427387f8f6217f6902b0e64e6481879a5bb03c  openroot/bin/0121_uf2conv.py
bb2814e376dcdd9942ab3eadc2a36661a5f5d4bf777d2d165aff641a7c579507  openroot/bin/0123__rewrite_proto_namespace.py
d971e00d4158789b518bada6114f49cb877e8d06bdbe601227aa5bfcde8118f6  openroot/bin/0124_analyze_map.py
e00e549aa17a30b1c3a563bc3c85d4e2076d793660f86e1711ddcb9604ea7b21  openroot/bin/0126_build-userprefs-json.py
10667762056b0ece69f7d94c2ebcf1a8663a5b272349df1bf8ce5456b3cd07dd  openroot/bin/0127_buildinfo.py
d8d54b94bf36b17485d9c39a879f99472ddfc0ff4557049dfbb5fbb27bb37384  openroot/bin/0128_bump_version.py
c7630b09f179e2a2830c9ad6c4cdd932ab553a0ea07518660c8a91695ba9b9c2  openroot/bin/0129_collect_sizes.py
379691cd47d37af6c2bedcfa63322be26fbbab74a69620645c7a6394429dfab5  openroot/bin/0130_eth-ota-upload.py
411b51a45973274b61eda39243eef699be97c0b90dec48d263110f512525a066  openroot/bin/0131_exception_decoder.py
8015ef111d347d087ff70aa2bbf0ff1ad03c50607b80f0a31bcd73cde3fd6add  openroot/bin/0132_gen-fake-nodedb-seed.py
f5656481f6a7b7ef67d48098118ba9064f6fc226f42551e7e29f43e9f6ad7b33  openroot/bin/0134_generate_release_notes.py
060dd1b61381e61a6192e4a00901373a7032c48b5b2e4ce0122a5f0e0e5fb986  openroot/bin/0137_platformio-pre.py
4b02dd7de49a46779063295bb395218c50fa9c71f19f548ef0594b22bd96fe19  openroot/bin/0138_readprops.py
9318db6aa4e97fe6f0de1a0c2d3ca172a9423eb7ffb4073291b983e39611ab3c  openroot/bin/0139_seed-json-to-proto.py
993ff3dfb956c715f7d51f5a964fbf3750133ebe83efed5f8aaab254e88221de  openroot/bin/0140_size_report.py
9133a08d8c42cb898bacb12ba725d72538938fcac4f830271480d540c9bc113a  openroot/bin/0141_test_size_scripts.py
067b9ade2484f5e6d20830e4a4e6aa134e18fb6ae679e8d55f032e85d67d4e06  openroot/bin/0143_filter_c3_exception_decoder.py
7b10d3dc17b6edc1c4c984efe4b37f2826362798ba5f5925edca09fc35ad1432  openroot/bin/0146___init__.py
08569f92dbf7553a6fba0c6c6d58defd05987e3a3edf955b4f74ba378033e8d2  openroot/bin/0147_core.py
1515184fded3e7ae69a5ac1899b0fc288f366dbcdb3b10c007ac5c61391d5f0e  openroot/bin/0148___init__.py
0b9f2239192efcfcb7b9bab21414e1bd1c8a2c97ec7e9780c77f0eb05c1f93c8  openroot/bin/0151_core.py
3694838dffbd25554033b6173f4bc33031e63ab45671f677394812ef1aaecf2e  openroot/bin/0152___init__.py
4bb8bd0e7f5a4994b4306fb65abbdeddd57d4c898fcef427e638e1a7db7fb9fd  openroot/bin/0155___init__.py
5e980e2254d02e0cf73ef0d3da7ee3d8dcd7feb54564b0881bbb7b6f675d85c3  openroot/bin/0156_build_env.py
9cc878f18bf7caed474b5c8276c728baee81e81e7360159d57a6e1aacee02fe1  openroot/bin/0157_cache.py
3d7cc67c1994177aca4108c200c709d5fb33070ea768bd674caf025e1222ef3a  openroot/bin/0159_exceptions.py
27eb135aa0be5dfb0a420cfd9b56f2a4c5993c722db121f320dfcd59e2119a13  openroot/bin/0161_pyproject.py
f57c4e5cfaac66529c7933f6b594bb23bad78e8767a9ddc6ac843c534fcbf013  openroot/bin/0162_self_outdated_check.py
1b1c11926fd3401b4f6697e954af6be92f5d032d835675600d51c929388f6759  openroot/bin/0165___init__.py
8a2b2dd84a7326f0d5221300c57abc8859d306c89901dea2a65c5f98d6e83729  openroot/bin/0166__cmd.py
5be1d6fa5d358320ac9f190ec826eac7bb31ad662805b2ab0ec2a455540de8d1  openroot/bin/0167_adapter.py
c416ae0bebd44aee46b09b310f8f96f8968aaaa6c1cf430de99bfc3c0d8df212  openroot/bin/0169_controller.py
82a31753cc34810b8442249dbb7620fb4bddf645bb9eb58a6cb71aef9ae17861  openroot/bin/0171_heuristics.py
73d79a62e7efd6948b97443c40d70c88c2cb1f85aab8373174fc8a8e6238a296  openroot/bin/0174___init__.py
d64dc2afde6f0b1c464460e58eb5b7c0c76965d2f73617f4bb59fe936a9db026  openroot/bin/0175___main__.py
82efc40952359b746ad32b69b0d13ad6181019c29a380b7d46cf46f0ab1308e2  openroot/bin/0176_core.py
2f06cf92c73403524c6e2e979ee3dd301527f375fb04fb85356a8f184288ebdf  openroot/bin/0179_resources.py
4732f2e90402765f7bf3868585bd845fd10a1822638343f73e294675e5d7731f  openroot/bin/0184_compat.py
3f6ebf5d5c9cb8c4d9d51da634ad594445733399af4f375a6c15dfc99554d4b7  openroot/bin/0185_core.py
486f2385a184e778a20fa078f69b76a704effd4bc295c89613e379e28476a785  openroot/bin/0186_idnadata.py
6a652d91d8587101bc66bf82a0c33f91545a731922bc2d568313756fadca29d5  openroot/bin/0187_intranges.py
fc251abcec686e76f2346d852f21e837c4073f740cf56d6d2aec3b7aaf50c019  openroot/bin/0188_package_data.py
440f2072a2b5ed8a64c419cdc172556b5a1ad8bca058381f1759c0d4d3f0de6a  openroot/bin/0190___init__.py
92d789bf4de7f6d633779a28df1628a554e8e2f45a031a27050409857a21659a  openroot/bin/0192_ext.py
d20d4fce9d2fb66044989e70f45decffe24c55444ff114b81b571ce5345a02c2  openroot/bin/0193_fallback.py
42130474fbb65e882b2735774b42964bab7b97423d93c11e0d1265e1f9f0f3bb  openroot/bin/0194___init__.py
ea17c461701ff2ffc817ae7e94569d24e30889e04fdb120ab721178c6d67188b  openroot/bin/0203_errors.py
dd705c4ac966f984041043bfcebbf817a751e70471b3812b26f274be33417c63  openroot/bin/0208_specifiers.py
af40ec85505ff913b58d72465fc0b84e297b1755d6b7e6e47563209af1226988  openroot/bin/0215_android.py
5999a4500fbe2f724d4469b3df6b37e587e80f789c6bac4a20f74257f1e12dcb  openroot/bin/0218_unix.py
5ab9dda527ba8b57245ff490d4a6b10fd093286cc3d04b82385c5c6f0169a0b5  openroot/bin/0222___main__.py
b4fc74ac9093219f62a1180b3581b8a627c26c0c1345465d76f2f0f8d7c0936c  openroot/bin/0228_plugin.py
8d8fab6b19e6c91c81e7baee022b6b25153311ec6e021193a6033282ac7aed9e  openroot/bin/0237__impl.py
9d9df14f61e842310e2f8396ec2336b415adae97dc95ac6e4b3ddb4197ff99b2  openroot/bin/0239___version__.py
f7fedf71d61f3050dfc8ae210f63ac4608868aaf240f0759706b91aa43f94758  openroot/bin/0240__internal_utils.py
2875df9db347d857b8add1892b7ada2f83b79f1917c9494b8b324904482e8527  openroot/bin/0243_auth.py
95110ef76cd4b977b4827929b6795646d355a9d27749e37049b1e0033a8c6b44  openroot/bin/0248_help.py
f5fad88402ec2c19071fbe86f8762abc0becb1296ed42d5becbebc700b3e1398  openroot/bin/0249_hooks.py
fd94030894c9f123f79155ae9d2a81b1164d3f38f673558556a6ddaf4f29cf75  openroot/bin/0251_packages.py
f886e6855cf4e92fb968f499b94b6167afba0fd5ce8d1b935c739a6d8d38d573  openroot/bin/0254_structures.py
c69369a71392a249cb09dfe760a44cfbcd10ae1c64665b907e21f9cce50c8e2f  openroot/bin/0255_utils.py
ca85fe778493bf01860a24111397090bd0ad7abebd4a0560a82971382bd23fb3  openroot/bin/0256___init__.py
751c6320bf926c5558d2adc88d232b7e00531eb9b52d90e02ceca0541c226197  openroot/bin/0260___init__.py
7db99ec9eb447478f313f571da5d6e2bbb673ce84cb365f59497cedefb0a0e90  openroot/bin/0262__cell_widths.py
5ede3b41a7022b062bbb38c38be80e06aef6e0945e0e3f429bdc548b97ebfb7e  openroot/bin/0266__extension.py
1d66713f90b66a331b1ebcaf01066c79f9557d0a06cec28e1f3286b0b0fcca74  openroot/bin/0267__fileno.py
44e4f43cb0b618c5a26a559992a2488e662aec83518a34109284a89164da0222  openroot/bin/0268__inspect.py
d41c88d0f035669c5963708624e2b9e218e5ab85fe073fdba088c8a8277c2a7b  openroot/bin/0269__log_render.py
855ffa08b7683e6d2f6b6d96a70e332aa334458b33dd36715e3d0fa12fbd7834  openroot/bin/0270__loop.py
71d7afd4940a67426f960b95f62a478339d3767be52335050c16f422dd8fce32  openroot/bin/0272__palettes.py
7af0edf10378945e428b0ad421794e2429ed8ad0423ac23764b3c42005512c95  openroot/bin/0273__pick.py
38df84f99a924a1799f3c56b297d8cdcf5e915b18451464f31afc07f497ee1fd  openroot/bin/0282_abc.py
760fbbb98d2e90c2cb95412c04344bbdadb6fec4202090f804ad1d9991c51ee8  openroot/bin/0283_align.py
9266af05cfdd9fbdcbfe0ffcbf1592c18243daecc15ce5054ed24e7e96dccdc3  openroot/bin/0286_box.py
2ab4248f9f8b821082a492d23502320198e775ce1b9c4a8e1268b962e67d5026  openroot/bin/0287_cells.py
de585091d25bbd63e82c33be0276089805a626f579765818342559f7b39168de  openroot/bin/0289_color_triplet.py
b7d6b366999131553972985505949284db26071776f880167134e5868afe135b  openroot/bin/0291_console.py
1144d25052d06f163a666a3fb1d33ee4bb37db7bc81d305f37c4cfba5a9e1d46  openroot/bin/0294_control.py
4e5f531cc0d9f8f9395a6f2c23580683f5390e1bac9b10fe159d1f51b714d16d  openroot/bin/0299_file_proxy.py
bd512829d6b0a094630056b23f05e43013cbcbb4524ecf9fe38c124034769c9d  openroot/bin/0302_json.py
6a3912140b4456ff44153705b3ec38b997dfb7b9c45e13732fb655760ad3e6b2  openroot/bin/0304_layout.py
ddeb8628fe6ce353424306928d39c9c6eb398993078f1a483345ba7c2c6b6b7f  openroot/bin/0308_markup.py
48efc44c114a6e0de7fc080ecd79b8d52bf7e98c57032237fd1f8a398dbfb927  openroot/bin/0311_pager.py
9489ef4753830d3d9fdd464c7cbd60aeaedd63fa4374a1f0e1b75480e19a3386  openroot/bin/0312_palette.py
f6c425d3484f22a1f91b68002d0a3835ea45c293f493dc13facfe03a6b39a487  openroot/bin/0313_panel.py
d1f35a4bf68445add43117374f958ca4dfecba6b43c5f6a8af6cb7a1fd5fb419  openroot/bin/0321_rule.py
9243e987761e019068f97fb8c0fa7c813a99c94e3ae8d2f06410383d94d37b0a  openroot/bin/0326_status.py
6664fb57b30c08e60ac3b4c663d4992f26037fa25d33e5957f4ec5755b958532  openroot/bin/0330_table.py
a0dca15e119a82d0e56c3c9eded56eddeb16396934bcd92ec45c3efee9e568ad  openroot/bin/0333_theme.py
d318132e8cdf69b79b62d709b43742e50917e4855411abe2a83509261e185459  openroot/bin/0334_themes.py
7345a607f2f4e3f51f65b2daa07f7cdbf53fb3b7a8b3128c5220159833dd4585  openroot/bin/0335_traceback.py
cc1f9242f272764b3bb50d32230acfe860f77d035249a3e2abbcf0e321794f8d  openroot/bin/0346__openssl.py
802785f3948efd45385a83f0607228cffb70f9e33f1153a42c5a7c385b02ec30  openroot/bin/0352__request_methods.py
79e43bee726317dedb3fa4af08ae209b1e81a5064a53cca3bccf80203c19757f  openroot/bin/0356_exceptions.py
da9903ba3b7ee824d27ab4b05df9314ef70cf7713696c3471dbe09fc07ba34d3  openroot/bin/0359_poolmanager.py
7848fab57f7c669db5960442f310073dd888e5b45d1e592e2947008eb53253bf  openroot/bin/0360_response.py
a7d2a2f5ea35b4504efa3a95ffb2a6989eb444aaa8636af86a8d1299a1cbc8eb  openroot/bin/0369_request.py
bd013adfdba81218f5be98c4771bb994d22124249466477ba6a965508d0164e0  openroot/bin/0370_response.py
0e2ec353bce892896d6a94ff1744a3db57df631c1a4bf704e5aa4eb70b9e7b20  openroot/bin/0373_ssl_match_hostname.py
133e0ef2947fbd3f1d6a7fc5bea0584ba7600df05710c7d57ebcdc754a167e2e  openroot/bin/0374_ssltransport.py
66bb97696295cc010976a347dcd121d26ac7af0fbed956586f4cd7d11a273590  openroot/bin/0379___init__.py
967fe3690b602e545448563adbbca21c6da00fb020697cd129a12515587b7c34  openroot/bin/0387_exceptions.py
30934fa5f23170ef85821c6905bc641b5ac58907fa1ce51b5785399aad07167b  openroot/bin/0389___init__.py
978b425ccf1ef5a3c2d810fab2322bd1d793f89fb3e6d1e00b02fea757d2d0f1  openroot/bin/0395__mapping.py
ea5a2f154136f6dcfa12c5775d8638860a3327bab524bedc7cedd43a58274bcc  openroot/bin/0398__mapping.py
596ec35e2ca0ebcba9fd8343ff0a51625af548786257815f24b41f7e08613314  openroot/bin/0400__spdx.py
77cba9166cbfcf06829a56d61150652d715d76df19c3c739485a7178e66c75fc  openroot/bin/0402_file_cache.py
646d9c334de795c36bb3e586fd21535b8ea2b31f6cd86a399540fff3e8afef4a  openroot/bin/0405_autocompletion.py
3d370a49df89ddb51a9730cef6436f6779841a22578b1df64387cfc24c525c87  openroot/bin/0409_index_command.py
2a60a9a6791fecce92bc9215addb349e0f371c5319db3e18ea9835c829f28c33  openroot/bin/0414_req_command.py
109cd921937252d2658e9dfe5a372cc88aeac56f8752c7d6ce1b96f389ff4eac  openroot/bin/0415_spinners.py
b0414751a5096eabfc880acbdc702d733b5666618e157d358537ac4b2b43121d  openroot/bin/0416_status_codes.py
85514141ecd0df38f813276859b1508ff69f3d4a6932deebf493c0958db653a6  openroot/bin/0419_check.py
ea034e1ab5569ce2d4d79cd49c088db8e3217fbe9144866f09d543d1d7a03d19  openroot/bin/0421_configuration.py
2d4355a1bbaf09d6a08cb06e3c16b11de0621c48887b4ddf4ceda6e9a842f2ac  openroot/bin/0423_download.py
7f1a16f0001cf9b02a07f7d774dab656767725f5a414c83e6d1e8b71d0d53bb0  openroot/bin/0424_freeze.py
661be0680bba9a4cadb36e4bdf799d070f1d7e2e74ad33493982cef0636033b6  openroot/bin/0427_index.py
c30b47610dd4a03c5770ccac8d34676d63bc65e83f0befcd93d4a031f0c7020a  openroot/bin/0429_install.py
d78e6286350affeee03fc3bae573c38bfc4c8658798677b5a6d90775f9db0274  openroot/bin/0431_lock.py
cdb32c5ff6004a3ea45c0e972018130efd1b18ae75c46f825772329d925c13e7  openroot/bin/0432_search.py
2fdbc4cc9fc4e36b1c17f1e08795f81e4dfd9ea2432b11a0e2eee094361b3567  openroot/bin/0435_wheel.py
1eaea4b7a8170608cd8ade614d358b03378234e2a807e374a46612a9e86b962f  openroot/bin/0436___init__.py
97e39308022cdb996c6a97a303a218a4f67148ce7e0444f8b1d64392a97c8e26  openroot/bin/0437_base.py
458c1021bbb1a4acba3a394164201e7f1a4c0daa28714438745b61786b224ce4  openroot/bin/0439_sdist.py
47b19cc7fe0612848423e89acdf0195443c6dcba7a99b653e256c00fa36301cd  openroot/bin/0442_collector.py
7d7f654657e2524a02f7aac889883833f6c3595354a5a5f64f35f1fc53fe6a82  openroot/bin/0443_package_finder.py
8e9163e15d34ac3f48477bc0f53aab1a4c1c74d545739f0bb028596af81ef496  openroot/bin/0446__distutils.py
046b8c7a795c413f22ee3f62725adf742def4b082f86bf208e7f79e5c0b2d7ab  openroot/bin/0451_base.py
34eefa66b7d1dbe2ca253c9a5eb990a0686624c02b00bbda72b9591d58920d3f  openroot/bin/0452_pkg_resources.py
023982101c57fcc1fd7ff8d58c818d08524a60261e4847b5f32caf371e2e44a4  openroot/bin/0453___init__.py
f514b74d0017927c0b77c24e3995a56c157a59916cf6a9fe600624d1543c47f4  openroot/bin/0455_direct_url.py
1be3bd28495a6dc5ea6cfc1f13feba9735f97c66a18771aee83024cfff59849c  openroot/bin/0461_scheme.py
fe2f868ffc3f170640bd3b3b5a18ec9410c3ef427ef219887635c1c88f2e1194  openroot/bin/0462_search_scope.py
21372e2eeb3bebaeb084d54948836e34c459ccda061f09aa8519cfea112ed289  openroot/bin/0467_auth.py
f22959c535819bd2754c4a6ea45139e954398ecdcbf35aefdd7d2b6707c13d38  openroot/bin/0469_download.py
cbd81592c7490928e72df633b3f9b70d8500b65de173f93ec453c305df4380eb  openroot/bin/0470_lazy_wheel.py
448b2a48fefda253dd3a0b4f296fa8390dfae08095a297a103a45f1a445f7b6b  openroot/bin/0485_base.py
335e6e50f221e4da4fd6d754181c516aeeaad59004b48f3e5f22c4113b1c15f1  openroot/bin/0486__jaraco_text.py
0e23522eaa6eaee5d46a6190c0e2765990720c62d319a5e2f4ef977fc7ce8b7e  openroot/bin/0490_compatibility_tags.py
92e24e7f5996f06e6d44537a8d66ab75d752fbda92691e7794ad639b1dcd4d96  openroot/bin/0491_datetime.py
a04425b660aae382d0e843fb345e5b67248c7fec0289fa32cbd8e5dfad419d53  openroot/bin/0492_deprecation.py
b8f8c0c9284a39b768b63423254ce9ad0eabdf142f0c86705187c71ea67b0e89  openroot/bin/0495_entrypoints.py
ea5256302e9ceff683fe2e2c76069a79bf939b7916a5883485b6bf575f8e2e71  openroot/bin/0500_logging.py
4f8ab277e4d66f9e3020ee7f0ddc004804ed53b822d3c20611affea5d151ec71  openroot/bin/0503_pylock.py
f37c11784076adc9ed319e552ddedab1c6984a39ff90b765402ab120bc5690f3  openroot/bin/0504_retry.py
997f943f2c3530fc61c14c4a85ba96597ef427a3c75c0263555ad19c6d21f667  openroot/bin/0509_virtualenv.py
500aafce96e2d156d9a3751beac904799030fa8a08651fb35ff5a909bc720a85  openroot/bin/0511___init__.py
c10f781e47a9fbb91610701cf8d6cc2619b3784ce0100b71781c72295cd9a1ea  openroot/bin/0525_resolver.py
73bdfcb1500a17fce187214e20a98b94c69d46f18e7c476a7282a3ce7c296142  openroot/bin/0530__dists.py
1f7a952d7561e0b5afacfbeefde9177f775f6edc2796134940fda9c57a5c71f5  openroot/bin/0531__envs.py
8ea8a8c68dff992b4fa7f7904782f60ef640cb278b7770f01f03e1749aa9c879  openroot/bin/0533_chunk_and_seed.py
444fb46b0b9d41c2780e3cc619eb6bdf8469c73058795c004dfe2d29d7859a73  openroot/bin/0536_bench.py
2e148ec5328d67a5ba5d6f6139ab6cdd46c6eb27658b867ce9c6108080bac1f5  openroot/bin/0542_fuzz.py
1f3060bec42ef1626ebf010735401ae896a0c001a0dd056be21666128726fcec  openroot/bin/0543_generate_legacy_db.py
d7bc24e7c48f79567233acc71d0480e1d1ffb04182c5e4275ae7fc712fadb671  openroot/bin/0544_helpers.py
85d7816047522d99a3f90ebd2dd04a47d80866c6b385ea91d8a9e3164ee3b36d  openroot/bin/0546_test-auxiliary.py
70c5bf0aad9f783bc21125b9d5c5ebc803223cbedd52379b06ab128a15defed4  openroot/bin/0553_test-ivf-rename.py
48ff84d418568220c06690d4f6b7e7cee849e20fc438449e228b099a8be909b0  openroot/bin/0558_test-metadata.py
ff37c635e8a05eae75247ee6b28ea4653c1de40d0feb5d728fad5ebf8e08c15e  openroot/bin/0561_test-rescore-mutations.py
e0aa4d73b29c83ee8502b85934a20d96cb253f611d084564132b22e4154c5b28  openroot/bin/0566_test-correctness.py
f76295c83bc7a56b86cd894f700d8e688ffad7b9c452e44e4d60100f1e5b4c30  openroot/bin/0574_bench_delete.py
892b1f34a1a34120d4680cf41442eea85f846ef9d0fcf905349c8aa2e9f4651b  openroot/bin/0575_test_smoke.py
e9dac95c73b87e57bd305c1aea3f40aca43ae112a9ef0e8f05c0cfb8f92ce8c3  openroot/bin/0577_build_base_db.py
8fdcc8c2a0ee00b1220072b3b4fcf23136e6dd8131f0a2014a53ae983ad6d284  openroot/bin/0579_build-contents.py
a6effb2c4c94a65eddbc9d619779460e8df213256a9cda94cf78fd60c1b8f7cd  openroot/bin/0583_fit_plot.py
37a668a9cec431c09cd7eeffb658560e534cb12f8d66a71a79a2874b3d68d7fb  openroot/bin/0586_axiom_cli.py
00990edd5e60922d8894eb85dd575a4cd06780561aa4b99c32712d1e3d2761a3  openroot/bin/0587_merge_kb.py
830ed45943c247250cd8cbba4337d5a6bfc6b8b3f5fb479a8fdf9f29ae7d29d6  openroot/bin/0591_rmh_labyrinth_model.py
5eb4d249275ec6f5b3eb88cc94f0a0f9aec5b524f4b502b827331490c452d7ab  openroot/bin/0592_psychrometric_model.py
f81055587c517bde5f9820ca630e3f2debbb7005cad52df7d460ff18182d1582  openroot/bin/0595_nomen_core.py
8b2df8643ee7f713cdfe3da7f49a183519e575accbd121c16e7c0983fa59d42d  openroot/bin/0597_canon.py
63674cf3b88a179232bb8fdaa186db1eb7c5a020387f057edfc7220af76bf201  openroot/bin/0602_fusion_sensor_wrapper.py
30a42a3b648e0845e0f0a3117256bdfb4af2c298010226bf67289c714e9246ab  openroot/bin/0605_synergetics_engine.py
b54342e5c447de0e7a34d8a7e8f0a89e86767cbaa71838198685533a8f69d8b1  openroot/bin/0606_build.py
e8375e42ae0a45c84f7d7e8d5b8ee365d7da5a5c4acf2784a1f8a83c7a64afad  openroot/bin/0624_openroot_classifier_loader.py
e5dc330c934cd73e30b38e9dda7fda584b84ba9e3d311a8e0c5163e6d6172395  openroot/bin/0627_fusion_core.py
a5cbce0b0f84ec9375dc6e3b893b1bd263a2dcf09c7966c920728b028dbdcf5c  openroot/bin/0630_kai_query.py
46df74e6329e55f3d125c0ff5b57a17e082131e7bac24cbdc8efc6016fa1252a  openroot/bin/0634_platformio-clusterfuzzlite-post.py
34af311e35e01a377d16efeddf85c3d6d5d4609d603a8a1c912700f7b600f3bf  openroot/bin/0635_platformio-clusterfuzzlite-pre.py
80955ed531900217e5f23d58fb229b4366b12bfab64e7dabf6cbe3e2c6415187  openroot/bin/0642_nrf52_warm_region.py
7fae747f2e969a2ffe2e6642f50494fcf1a756516a6709dd5374dc65abe46c19  openroot/bin/0650_test_memleaks.py
5626583bb82fcbd958c77987c54677975092a0f21664aeff37d24f012ff6fc12  openroot/bin/0651_test_posix.py
4cc799386b90a44ae899c8484bb8522a2f859c0791e05eedbaa61ae818b4c51f  openroot/bin/0655_git_pre_commit.py
0863dca5badb04361414e4dc95945773c0af65c58901e24ce0cff5678ef3e52e  openroot/bin/0657_print_api_speed.py
aec488bdc12ec4fe178ced161579d7055851e1b36bd50945c82d4c67ec1b4077  openroot/bin/0662_procinfo.py
548cfe1454f293eef90b98375722303384a5a768063b83fdf3a1058ddd305789  openroot/bin/0664_winservices.py
ccf4fec85bd7cd20e9c941190722d1dbfc3845b13c7b712e9fbc61e67dc48758  openroot/bin/0665_chunk_sender.py
e65ca5dba84198eb40f42594de06325c19a469c9bd4dfe7315d07a048ae456ca  openroot/bin/0671_build_spec_v1.py
cde8d338efd5f2f4c1285e9f7e5a1abfcb4297c909bd7e3625d712f164ae81dc  openroot/bin/0675_makefile_gen.py
c629d2d5b8967dc152b4266a862b9cfeccf51d564d2d25232152f49437d06ba1  openroot/bin/0682__compat.py
013cd1095d473657c052f6b9aa20d73fbde325839c418e338d5cf66937d8671a  openroot/bin/0684__pslinux.py
a4c47099ed38c5a69cb0b2e03ced222d545978d1b16a00d015e77fc04d6979e1  openroot/bin/0746__psaix.py
31cbbb4dfe98d62d20438157bf8b7483c71b2f98e8004b218e0229cffdaf2122  openroot/bin/0211_version.py
01a8035aac1e6b6c8159fd74282f69b4180ca4c8f12a9f3200102687e3503959  openroot/bin/0223_console.py
29940c9b2a3fc643889101bc83ae8b6049018756f1edad07c8608172f848f44c  openroot/bin/0225_formatter.py
fe406b389fcd4f94e5d0854cd2b03d73c7b2b0febfcab946cc4408d1e55807e0  openroot/bin/0226_lexer.py
e71ed987d62553a212277d5d33076e89a6a76f97566672a0dccc8442cb1e3674  openroot/bin/0231_sphinxext.py
59b7561a1626fd5a2c6f40c3c56f651cd3e02135df593b10987b7a732f516dc3  openroot/bin/0233_token.py
6a5fbfac17a646e1af8a7b2b33a6ad36c1d3989e8351bc36e2ad8ed91bb57017  openroot/bin/0234_unistring.py
a11b52a62028e6333dba59ed92f55b81751d8805b9ee39ee60607bb7d7d8ba17  openroot/bin/0235_util.py
783d46d11a0c677900d25c9d930ee8a3496670aaaf0f5861cfac8e96048a9bcc  openroot/bin/0244_certs.py
a485896c874927d185b4d6edc131f421ae37563ea16021098f60ce2ee7b5e453  openroot/bin/0257_providers.py
a4d25fe271712e901e2b1941522d86123d1ad888f59e2918d1469b4ca5deb13e  openroot/bin/0258_reporters.py
f82f0e2bbaf19f7b0851d570c59041a5e1e12335f4788f9533731e9987da5e6d  openroot/bin/0276__stack.py
05268344833004b2139ff9b499344b3ea304e6afaab8675232e60ca587982707  openroot/bin/0278__win32_console.py
1654aca26e445f42d5900dca5b2df8c879c27cbb6a5fe6487a95ca87eef4ae97  openroot/bin/0281__wrap.py
95d6d51cecca24e9df95536ebf5c52ee0e9d2d7d84df03275e474f6e9cc94dcb  openroot/bin/0285_bar.py
73fe7a4f171e74662a0dea4704c4ee65d5088a38ad010827a31f9075ed19d6aa  openroot/bin/0293_containers.py
921405aaa6a80ecddba6b32a5a91f0f273b95291b60cde90b6e4dde8bcd9c187  openroot/bin/0295_default_styles.py
78328847097ef9e6742f0a3675ad9146d7eeb5719abeb24eeb50a5e4e912e7d5  openroot/bin/0329_syntax.py
dc5162e65002cfd79fe268d8296e12c38f1ed7986f76000e204bc500d51c7edf  openroot/bin/0338__parser.py
f864c6d9552a929c7032ace654ee05ef26ca75d21b027b801d77e65907138b74  openroot/bin/0340__types.py
d05f320ed5f1dd4ba7866f3be0aac070fefab2bb0cf7ccbb5b21d0c02ba565ba  openroot/bin/0341___init__.py
ac01f22980fc33bb7e6d77c6f1580e55add3a5f85585bb78ad94253b8e58b8ff  openroot/bin/0348__windows.py
24ca35b60d67215d40789daf10d0bf4f17e5d1ee61e86ce5f43195935ad645ba  openroot/bin/0349___init__.py
4f57301f7461cecac187a073dc03865436e846c13bbde8a3a993d75d04d1d918  openroot/bin/0350__base_connection.py
bca13ca2bd269aa82c16955bec5626b3e9cd39508f3c01227e0c55ad368f072c  openroot/bin/0353__version.py
53c78d67e9a928a1e1ae56c7104893c7180ad7a21e8e111aeeecf8db2a80fdd2  openroot/bin/0358_filepost.py
6c7307e9f36f6adc173eb2aaadc9fbe32037a5459ca8f0e9a672b52dc2826cff  openroot/bin/0364_connection.py
9e7024a9b8406a43a217be6bcfb5b4b9d677f047a1fee0fc7e357be0def71442  openroot/bin/0365_probe.py
faa792d1071e8af6b3bc110a0cd142008fba00271d0ce1384ccbe8ed22cd9404  openroot/bin/0366___init__.py
58e7081d56b129ff9d55bf3d9546e9bdca5e33bacd605fefb0ab0238ac35d19f  openroot/bin/0371_retry.py
fe987c22b511deca8faa2d0ea29420254947e30ce419e3390a2c80ed7186b662  openroot/bin/0378_wait.py
98bdbcb33cb52af137349856a2be633666aba7c830a650d4fbb8301996398344  openroot/bin/0382_request.py
95c9991afe6c2873a7143fd1cd9c2f9464a3d7d31e03ee6b08ca5d7f64a0c3b6  openroot/bin/0386_criterion.py
dc9ff3916fac0f7118f8194d5e3ca59fffe78e9c87e67d146494fab95ec285e0  openroot/bin/0388_resolution.py
c1b20c137e461fb6c8d41f6b34f245a964fe8a3fd102964360f52567271a2f30  openroot/bin/0394___init__.py
bf18e7d5c38772520a24ac68ca206c41363ae461db919b5946e290d8054229ac  openroot/bin/0396_python.py
f6b9aac2d62efe58d5916ebfa0ba9b0bb11a5ff6bc613ff22ee9daf9e4b4760a  openroot/bin/0403_redis_cache.py
926bb711665b7c17a06b5a036a69c625303f51a7a384840db8c8f609598c5eed  openroot/bin/0408_command_context.py
108144c6b597ff59eb97521bfbe18ea2bef4598a8bb5db870727a76f5bbdc47e  openroot/bin/0412_parser.py
216d4f1f99f614fa940533fb50b43962efb0c8d34ef57198de0d4f4f844cbb8e  openroot/bin/0413_progress_bars.py
68d7826d0bab1968a17e142aec1a9a2d71ea5834348b7234e0e4bb9312baa654  openroot/bin/0417___init__.py
a0b54921f2969832a6d12b101848b7a68ccd8aaad78d3adab3f7db05260aa410  openroot/bin/0433_show.py
92020413fd4dce36712c1482fafe6ceb8b8e15995512ddda3eb8d3b4beb1d976  openroot/bin/0438_installed.py
b73c0c1ff7e141eb9bc0ca877528af6ac83571181349b360d8288c567ccc9b25  openroot/bin/0441___init__.py
f02a538edc5a0b31d20ab2a96b15a71c4eda29c26b4494669ed47564b572b0b9  openroot/bin/0447__sysconfig.py
84dbe73073972c0c8d9738ab5a13cbf4dc760af0aa6b589199ae8eb2ad587d5f  openroot/bin/0450__json.py
e53ab0254d183a8828dc4b083e885aa90dd9e217d4e0134dc81601109b3a5b1c  openroot/bin/0454_candidate.py
3f07a6606d4bdbb04cd1fd4a3fad6b9b6e304a110d172c6a943d535aedf86a57  openroot/bin/0456_format_control.py
d5275f0ef37b00b4ec6f267d10eb0dcb518f8ab3f59fa1231f2ccfad9c8b4a1f  openroot/bin/0465_wheel.py
14ccb4e8ffffcba8cc8d473ccf765c41d285fa9999db3335e3fbc17873c68542  openroot/bin/0466___init__.py
5845600e623ef7bdda9f0edd85e1ace473753fa406cd2fe41e566561acc243c3  openroot/bin/0471_session.py
002b177759aca8d0a2747557b2eecb1d44abf0d81aca970e290e0a1be67fc093  openroot/bin/0472_utils.py
c82d975ad87a89e846184fdf8fb5d124b8d5281b13206dd9a16464162deb3b07  openroot/bin/0474_check.py
59c63dcfb0f7ae520a5f5418f3fb519c0b12fe9a1e6e218676d43b109e49410a  openroot/bin/0477___init__.py
74298e1edfbd45a241abddb52f8b4c1f73e62010deb46a659db8d1297986b74d  openroot/bin/0484_req_uninstall.py
58208f2679a83c7cfb92261e3eb11c5407a7da50e9093f56415226a071d608ef  openroot/bin/0493_direct_url_helpers.py
181078da96f199481d4406d280b4d1ad64046a9c8b0834a3c53db50cde108d4f  openroot/bin/0496_filesystem.py
b0487c44924b612751bd3a803b84c754f3c0f9848354b0f8488f52a3e6f15f55  openroot/bin/0498_glibc.py
dfcf9b08e2521e2a6943bafd46db6b307c5bda6bf710046dd46c3c905996ef78  openroot/bin/0499_hashes.py
f9f17face871071a79ee4c0694d9775f388172cd2009fe83d39c3167e9a4a137  openroot/bin/0501_misc.py
b39b6952616e9b05741fd2524f3af2ac863827040cf29686b7b4a6ede370b766  openroot/bin/0502_packaging.py
4d37aa0eecd2fbf04548db944ad556984da7183a4abaf521041264fc20905d5d  openroot/bin/0513_git.py
31afc7319055bde4a4798bf169cbea7ae8e791221a1755e3c53b12dc1c1c27c1  openroot/bin/0516_versioncontrol.py
a4cc14d7514ed63796076bd7fb0bc0e5f7720c13d61fa0dc723f6a11d8756773  openroot/bin/0517_resolver.py
e2fdc0d90ee04b56b5b5b31ba61a3d1e58855b87d198716ece3f1f6bb4e167a7  openroot/bin/0519_candidates.py
81646b720afae1baf479c17f3cfc4a7e7797133af493e4a896fd97f73dc6a23d  openroot/bin/0520_factory.py
b953db283fd1a9029d54e3f59744cffca96236e4161a6b4f2c7ea768f00ef537  openroot/bin/0527_wheel.py
8a63c698cc10e0b67759c5e8443e3b96e35d0a7c28ef0e01182ca14a8a228f0f  openroot/bin/0532_joule_probe.py
d22a1bd32a41973c20a3004b6db1972ff52448ffd04cf9f2d76f60009ed71223  openroot/bin/0538_ground_truth.py
fd8ac1cadee76a5badbe0c8cdd7006d13c63072d79b4204305df3655b997c9ca  openroot/bin/0547_test-cache-finalize.py
d6672c804186e45b4f92c51884064815d5d7e56f58a0ac5197e6dd71d54aea99  openroot/bin/0548_test-diskann.py
8fba3943445356ff3ba6adee2911938fedb375137ea548c90f1d957193ff7941  openroot/bin/0549_test-general.py
9bd6b6ab07febd7416e1a9c460231b693799988f3cc96b38fbf949ef3654b121  openroot/bin/0556_test-legacy-compat.py
7e4f8d2c72ed328ae1468b93f17db6f4cc818ab117b6f4e7a474617f8d6343e1  openroot/bin/0557_test-loadable.py
a7f619c4757c26bdb8a4ea550217d881758c071ec5e8432bb52503c769e55122  openroot/bin/0563_utils.py
015249f6fc8be43592ae690e6d9f681644320ea8be8bebba1e1a002084e6d4df  openroot/bin/0560_test-rename.py
e052dd94d337785bc2e5d4522c33d9f9274142697c039d7c1b287d8d570a9622  openroot/bin/0568_demo.py
8eef416f6114dd133af085495706a236ccc7b28139092e67e6cedc8b03eabe1f  openroot/bin/0578_build-base.py
3c380ad630f2437d368184cf4d65972ac6289b5d8a0df4f66e948968062dc2a1  openroot/bin/0584_chord_lengths.py
f6531190f5754a0e7ab409e758ea866ded84494bc895bb2c3408e9fb85889ebd  openroot/bin/0585_pr-preflight.py
6213fec5dee47af0820695770796e346f621c14244a041660e91da9b6d4596d0  openroot/bin/0589_test_rmh_labyrinth_model.py
dce44ed7381d75906477518c2d01ae38d8c57b1d20d7920e6bd44194db6048d5  openroot/bin/0590_test_psychrometric_model.py
11ee14c0e9154223fc0ee2347a3c5304c1922c0dde574abd190bf02d50e4ee8c  openroot/bin/0601_laser_sim.py
5f9f655227522b0dc9159b58b42d56952a204835c747771582f1e851ffc4a2b1  openroot/bin/0614_LXMPeer.py
2c6550c83b1689f7400a8eeacedc1bf115961ddb3513bb90f99a83f12023cb0e  openroot/bin/0619__version.py
9a831368a4de880964ba89e1135b81b94f2bb9b722abd8514b312a67143c0fac  openroot/bin/0621_example_sender.py
150bfec1c3d364a0b09c52aac399489efaf57a6af4021cd1464c57f8feef87ea  openroot/bin/0623_openroot-classifier.py
02dd05b790de6246f7f99da845de959350b4e54adfe928dfba1bc2ff2c6edc4a  openroot/bin/0629_embed_kai.py
f1410525b75a6a1ac4505bc81e6337fb8ddcaa800755c32c066f3b56308cc49e  openroot/bin/0636_router_fuzzer_seed_corpus.py
0b472509f0fb8ae5e5fd0a4cf9ab50947771caa89c1d6412424c03675baf1793  openroot/bin/0638_esp32_extra.py
a957d37a92b3d2223b380d94802772270a8ae21fdf1dc191a20dc1b428f286f3  openroot/bin/0639_esp32_pre.py
eeca3aeb91fae9eb6b4ded408d107a129d1f10f61c9109fd60fee6e96165cc42  openroot/bin/0641_nrf52_extra.py
3f1f9d04ffbb63af76a89cf7a84d14cb5784fe2d0ca1f0ca97e2bd8a1b288926  openroot/bin/0643_nrf54l15_linker.py
b7a747fa09fefa8c4d25dfebc07ecdcbd584cc1ff07e7f8fe6f8240945d58036  openroot/bin/0645_windows_link_flags.py
8e17c0d012a72742e349cf7a04cfd87b90adb0eeab09cb3994a627c13c4db534  openroot/bin/0647__pssunos.py
2d42378f5ee5e7356ac0a5b476c0416f7511c8a8feb5517359e2d38143fce945  openroot/bin/0648_test_connections.py
2393a0f0aeba1674aa4e520a7a6548db17e1363cb1c194ed853320ba940508e4  openroot/bin/0653_bench_oneshot.py
04d132ff142b4503ba7b9a8a2bc3c6c64ea0767f88203b83c4a6fdd8506e58d5  openroot/bin/0654_generate_manifest.py
375f4abdde474a03069eec317d4e96ea5c3a3d9b9151700d52d8a08362580e39  openroot/bin/0658_iotop.py
ee05eecb028ea283f83dc580090a29bf6563014c0b511af5153b9cf0729a6397  openroot/bin/0659_netstat.py
f0a28db1d166d83fa9f19de545426d00fe50e4b68d0aa16b6b7af75cd1494893  openroot/bin/0660_pidof.py
a908942c020f4f6afc9d73d2e47f101fe27e7da6c24828ddb9894b2129fc4520  openroot/bin/0661_pmap.py
d6827ad9e0dc1a9d516076658f5d731eed802de5c9eab604ea46579ee151c803  openroot/bin/0668_generate_grant_doc.py
b06510ee884c9c63f00071aa71c1ba0a8868c0869d0e1936db4f6fbc6290d1da  openroot/bin/0672_desiccant_module_v1.py
8445987d552b7e23208a0583f1b7b156ec7bd842f6e3c3a58d25df9946568dd3  openroot/bin/0680_mqtt_basic.py
861337f388e3150b4317db138ff0d76814025c254bc1dca32e29785135e47bc4  openroot/bin/0687___main__.py
b8820afbd3be85b1fcb4ad9bafdcdc89285f84ec3869a51b6ee6e8cd27916fd5  openroot/bin/0689_test_process.py
59ef49b62b9570d6683007ea22e71e6d43d134205eafa813efc0996188bbe0e9  openroot/bin/0690_test_system.py
b999de5e566650e62785f5f68f02749872781deafe2bd2ef906f082824422a60  openroot/bin/0691_test_testutils.py
de461beb1121e0ef67240f16b5a7698a348377b6439b3f92455a17231d71d7a6  openroot/bin/0698_print_hashes.py
0e0234e5d84b1b805397bea3f0b1623ce9af8166dd8fce9df7e90d298e340f04  openroot/bin/0700_pstree.py
b6c9b626404ff62fefac254aa8ca895b382ba8b6621e21b844de30bc4c044abe  openroot/bin/0704_breath_loop_v6_radiative.py
aaf65c02ab33c1a72d0d7bf8cc9f43eebfaba8ff4fa0304d521b0e6cd701281d  openroot/bin/0710_settings.py
3a491732f58d475377f6fdda9b7fe40b22046a7a4449d6e497ab8e41b49d2a00  openroot/bin/0712_test_une_fixed.py
5bef60636443ea67013cccadb170cb909783df54d6b152bd61ebfd6dad4bb27d  openroot/bin/0714_test_contracts.py
617e3daca401ebd4ae049e44c5958e2ff48409438d48632762c7eddd8dd636ee  openroot/bin/0715_test_misc.py
2bdf172594614eb4551b45986502f7bd9135cb320e1f069918a2df7260064499  openroot/bin/0719_bench_oneshot_2.py
c1fb33d6cf97a12c9bc503386bf26d56bfaaf80062c9c6c65315d85e2d38f018  openroot/bin/0725_print_announce.py
97f4784bb0f18e03dd38628a5fcbc7831447fb4d8d12f13c7818a403e23c4bdc  openroot/bin/0729_procsmem.py
de38634d78b5cfb7b3c89626037250df86c9638b3301553293f32845141be30f  openroot/bin/0730_sensors.py
68d8c89b4596c7eaf26a8a85428f5009ee3126a925deb42fcd3cf5745e4e5f9a  openroot/bin/0737_custom_build_tasks.py
f104de9c3c4cca30ffe07446345ea307fa0dd37d09cab952cc45d33607d47175  openroot/bin/0742_test_une_now.py
079ccee8ce091799e8cadd13ba2fc6cd04ef061f8c8c6ed1939005ce43a65cb3  openroot/bin/0748_test_aix.py
6b0f19cb1d24fcccdf38fda9cab2dc023909ea6fc28d16bee01dd9c5d7e14a07  openroot/bin/0752_print_timeline.py
f1f81d372ec454a0e4aa11068a726d3ca16ae0af49e6fc8c721167b0c1a048c8  openroot/bin/0754_top.py
43952870c03baed00e701072f527c949c18e2aff174d029134af1fd60a95c6b1  openroot/bin/0756_thesis_chunker.py
44259d97b5eba36bb2d99137aa681d62e03c3cd56d2798a2d9bcff40a2cc2dae  openroot/bin/0757_diagnostic.py
4b5696fd8c9aa361628daa615dc26836eee21bb7652bfcc37619cd1a45309be2  openroot/bin/0759_server.py
93155ee1f079cdcdbe92952adb12581a65e368f030140d9308d493dc2d71c7a1  openroot/bin/0767_test_thermo.py
76fe8a605d2216b3523c6594ea7f1947a4e7a2cd2c0cceee8da13fead0477964  openroot/bin/0772_import_unified.py
f8d4ecbdfa14b8bc976186d72de1e28a2c0a463de528250224ada5c9ef1fa518  openroot/bin/0774_reorganize_postulates.py
897de37a8acee6ac9acc20b329ff5d1884cb70347ff947be9c7340d6bd5353c0  openroot/bin/0778_theorem_generator.py
2d92c102dd1f51977149f1d2fb2b9dfab3d225eeec05cdebb57ba87744c61c10  openroot/bin/0779_theorem_generator_batch2.py
68a4c288ce9d0c2cef4437b098674b2a0fba4a089e38b7f3cb41700d52e7dd3b  openroot/bin/0780_theorem_generator_batch3.py
4753dcd95ace019e99949d33cc6ed46cdd03c9843086f391905a4303eb182cd4  openroot/bin/0785_or_coder_node.py
ef1c2c122a997b4aed8d59ef48d2dd16fa59c9b5600cba010558138f0ba9c185  openroot/bin/0799___init__.py
b89b706a8a474ba3e0c04533e5c457d96fc62710da78527918d6812b9d0daf7b  openroot/bin/0803_Channel.py
78a99b0e23cfd6c2d5e0c8ff902499aaa927ac8c953bd4abec9a45f0a0a3a785  openroot/bin/0202_direct_url.py
422c4155c6fd0f61e3c04622ba1a4d91baa4f739cf45b53cccd5f4911d5122b5  openroot/bin/0204_markers.py
1bfd609dc4e60db44b6358e8e150c8f54c3e6f9204ae1fd0f55fc16d5253983f  openroot/bin/0206_pylock.py
00d607671610569f4194e41838753902b0cd548a53165e0a95ba1c6150569c5b  openroot/bin/0209_tags.py
048fdd28b48cc25925e7bbe5c599d3f285633e2502d96fec771ffcfe1f7d1de4  openroot/bin/0219_version.py
f2e36a2420b05ea6c4c79692b01af417291440e0432818a13b998faa2c356aaa  openroot/bin/0221___init__.py
2b9792911f064b5af93a45d74c739c57468cffac6993d7963442005be38e2768  openroot/bin/0227_modeline.py
9cd7044d1475b51ba24da1e61d24d310255814f70b7fa98366ed5ee2ef7503d1  openroot/bin/0230_scanner.py
3e5399aa5b274d5779f111b2e74be403671743f94fe5b1791063040539e8e830  openroot/bin/0232_style.py
fd96fd39aeedcd5222cd32b016b3e30c463d7a3b66fce9d2444467003c46b10b  openroot/bin/0242_api.py
6cd8be8aa123e0d3d9d34fa86feac7bf392f39bccdde5129830de0ea9692dd7c  openroot/bin/0246_cookies.py
b6fab91eb8b866e5b6a324181dfa19e6873af3c93c0f3b241366aee6c6560941  openroot/bin/0250_models.py
889500780db96da4ddc3ee8f7c3d1e178aa1a48343251248fb268cab1b382c42  openroot/bin/0253_status_codes.py
a6ef84262476201213af649078d3d16b4ad7863952b5f98efc6120021af7d34e  openroot/bin/0259_structs.py
7bf6950beb43cdaad6416f52b9932e0a006be8e0d5fe20cd5765a1db19313a5c  openroot/bin/0261___main__.py
9fe91c7adb04531d99526850adf78c35cfad79e1a1a6e490e45f153c1b32bc3a  openroot/bin/0264__emoji_replace.py
448d3ca52ae6e6d052ccf32f9db4ea6c3f5621a95a3a837977833545398bab56  openroot/bin/0265__export_format.py
00318aa75cadfa4ef414c295ead9ea0aa79c07ead2273a7e590b03ecb3cbfa48  openroot/bin/0271__null_file.py
20eb65efcb1009866c987cb185ee3992b91bebcbbdc55cfbcc5b175490fe6f66  openroot/bin/0274__ratio.py
681c1a0ff4b9e926e0a2922f6b2566a64d18dbcbb06360b905a6f5c25dc1a7e2  openroot/bin/0279__windows.py
b7be192f7c6e0c23f79e64e9f691f52f92e223671a909b9045095e1c225eae59  openroot/bin/0280__windows_renderer.py
d5520fb82f0082d296adc9dc42b8c1758a80dc9556cacbba8d9a35aeb87b73b4  openroot/bin/0292_constrain.py
59de1b42e6d9752cbaf8fcab45036e307b67d959258caf6e3d93d596ed9c9b1d  openroot/bin/0297_emoji.py
1bfb27fbc0ca8ccd6c1232c6fe8738a2f9169a25295af8fc6d78b4c9e7762e76  openroot/bin/0301_highlighter.py
b45dee90000967f37665b19c96a67e8b02e822867c7f41c7533efd8c0c89aa3f  openroot/bin/0305_live.py
e4a68f3d230ff45c5c5cf05c28ce1c19dff35bbf0f3207fe61b3159ef7d2c34a  openroot/bin/0307_logging.py
1e6ac8257f2c5914c76e087c33111acbff37564a8d5bfef4b3c68a3f965c608f  openroot/bin/0309_measure.py
832dd2ef6bb8151836cada28ecdd590d60c8bc1e2e9dbcdde625067609bef1f7  openroot/bin/0314_pretty.py
09473696453e5f9f6655d19f8cc0819197a218f2f7bb174e36384d245d93ef06  openroot/bin/0315_progress.py
9994cfa4953071f71d8100934f3de4c98f9f73bf5d74bc2dc7a1a18717e8d3ae  openroot/bin/0316_progress_bar.py
acd4fdc59ad56536085d90b43589f8d42250c1835b47e29e70f3b14e042f07c6  openroot/bin/0319_region.py
4cc514f2aa35eed872a9008faa30cb62983f514d64e6a55df96c2226f9c955ab  openroot/bin/0322_scope.py
628791784494871ef882ba9bd264926fd960861cac5a6147621b1b3154235cef  openroot/bin/0323_screen.py
a2d9ca78a18457e591950568b1f2557850dc0f100a1e9bc9fe12f34aee65ba63  openroot/bin/0324_segment.py
a27221a4a9658d11e9a5365ab313bc91782d632087524a5280a825449de8e758  openroot/bin/0325_spinner.py
5bd09ccbc3f2f253480ad95f729fabcb3313b90686c405376afefe8397c7bb4b  openroot/bin/0327_style.py
c969d0eab02f446277a991aa06bc52d925b64ca05336b3f449d63c4313853eec  openroot/bin/0336_tree.py
aacd12e34a097e45c84249dc7586733fcc587f4a5425bd7cd31192de340f5ed7  openroot/bin/0337___init__.py
06eee4aa49a9ba784bb23e710aef204ffdb992da0f5dc4a7c1ef151e4d46989a  openroot/bin/0343___init__.py
3540f87d529d483d36ae2efe75bd2d9ced15a8b3fd687bb3992b5c5bbb40974f  openroot/bin/0347__ssl_constants.py
d5947682a7c5748cd36085301742b99dfb60dba84ba94e67af5c874dd29bed60  openroot/bin/0354_connection.py
64486e76c6bc048b9b0f63345e8c4106c8f16ec5f0320512707ee843d8be8f56  openroot/bin/0355_connectionpool.py
9d764a3281ec8b898f3f92b7ae1d0e7486f13487fc019d2615411ee3a1b691e7  openroot/bin/0361_pyopenssl.py
c73ac0487ed1e4035190f24ea2de651a70133aadca2aec97cc8e36adc9f09aab  openroot/bin/0363___init__.py
2633bbdb69731e5ccb5cf4e4afd65605d86c7979cc5633126f50c92d5ad74a74  openroot/bin/0367_connection.py
bec5094693b49df2a4fb2d4e2a5805198d4e34918f824699ec1ee4aee129558c  openroot/bin/0375_timeout.py
822125b01a14b0a55445b6736fc182ac99aa5b6dd79ef8f668dc90545e36b258  openroot/bin/0380_connection.py
e7171dfbebe217165dda7072d1a2bbdddb49f53b21d7261953f4945f09f089b9  openroot/bin/0381_fetch.py
ee854f10d6191eecc4191b46e341e89e91f9b402181ec19c1cf6c9b7667453e6  openroot/bin/0383_response.py
ef6f0cdc4be69cf6d55d2ec4c5796fda432ee9bef012ca0fbad11f97eb9593f2  openroot/bin/0384___init__.py
a9c5cc866c7ffcc209ab5d201875b7980e1397c772f18cc731c7309cda0a970d  openroot/bin/0390__in_process.py
e14e23b40d17de23fcdee42707df9323e1c34b0f04f32f333181dad148db6da2  openroot/bin/0391___init__.py
d42c37ec5b9094d69c9f144a9ad94f5f89f22e85fdfedb64a39670b1c354659e  openroot/bin/0393__mapping.py
c7d79b72d7f2bc2005a4c4e5309e58c7070d601ce382aeb325a2a4366efcaf83  openroot/bin/0397___init__.py
76daebae82b90670034751968c2675f5a674b45b0c7ef141b4b410535b29fda8  openroot/bin/0401___init__.py
22a83fb4a03bef55ee30ed4fe2dfec0c79d228fce451bf43d03aae9c09b0fe4a  openroot/bin/0404___init__.py
fa826ce6529a3c3d915c1b81c817cabee9806b55cd615b61bf43e6d115f01a00  openroot/bin/0406_base_command.py
4077d468f99934cba66493d2e4999abe1f2335b23b4f7562f01615124a851f16  openroot/bin/0407_cmdoptions.py
5e34fb92363c192212324b051ec2ef8d2f4e81f8b97b1b4d95452ff9d5285823  openroot/bin/0418_cache.py
2e3bd1219e905220d724bdc838c15e0fefc9f7b1df8cc1a0124d23dad586bb55  openroot/bin/0420_completion.py
18ef6944ddf05c2da441aa2f2b9ed368b60131cdc896d387f763ba404c3a604d  openroot/bin/0425_hash.py
eff630b4f1cdf916d63c7842a7585a8d737fccdc51f5476c1c652e549cc054d4  openroot/bin/0430_list.py
0ac3a286abdbe9903a3baecbef4a177a82c778e7cdccc33cf07f60fbd6a8720c  openroot/bin/0434_uninstall.py
fc76c6d0e7a117c7708f8517fb157ffed5cbc203eeb3d3a33047f635346a05b1  openroot/bin/0440_wheel.py
be9f8903189683ffa5e45f004f425c7b2ef6b949e1f020f0c2897df8a92d1d9f  openroot/bin/0449___init__.py
b589cbf28c468b8692356babd261bc0c03fbac2eb2ba16bf33024ef31c3472b2  openroot/bin/0457_index.py
ced8b9502c75853d377ad62a9ba302a8577bd78725993817f2b4d94fd08a6434  openroot/bin/0459_link.py
2347854be7a26b793086b3af82ca61159b4d001d88c1767d4abf5fa7a22304fe  openroot/bin/0464_target_python.py
926457290ac6f44dbac50463db5d4b1de106a4383f4a5614f439f57c9f8031e2  openroot/bin/0468_cache.py
3c3758fb2fd9b596492c029c6963c8191280196ec35d1e3c7f468c454d23ec10  openroot/bin/0475_freeze.py
26c1b5a7709a55c5bc7237250f69038fb77daad56b35069ebd8fd49ca874d2d9  openroot/bin/0479_pep723.py
3eb58ab65c08f316d69d610a8d7b3d464ae9431dbf874d8005e7d84f465d7908  openroot/bin/0480_req_dependency_group.py
6167ecadb99f72b7d682a418cba3ae223b326fd21f2f5abfdafe33b26b355a32  openroot/bin/0494_egg_link.py
af8f816bf61cdee6574298b42b8a5916c093fd0a9d4afb45dd727edb4e1059a0  openroot/bin/0505_subprocess.py
685fde83dba5e5df1b302c5f4924b141c7ecf8ea4975b4ad62a647a32d8ad511  openroot/bin/0508_urls.py
dd6d5e1e3918c76bdce9ba1e6f634187823fae51805ccfafaf37cd84b9b54718  openroot/bin/0512_bazaar.py
837aad724021dc4df8cbee47ad82e5627399f5288f183212cecaa16910d402a4  openroot/bin/0518_base.py
5f79eb09c5537abde6652132fb5dca88f1412589a17d625d03572bf869f5abb3  openroot/bin/0522_provider.py
29f1e297f86c1035d7c7336a1428266bf6a63bb101b746d26910cb3471a8e84a  openroot/bin/0537_faiss_kmeans.py
7cd479696c70e8aecc1f8deb72f4edeb403a4bf4d1486c40bc08b79aecf275ac  openroot/bin/0539_profile.py
15ac356e763d64690044a0373b99fc7757a25ebef27c0212f00d05da0d099351  openroot/bin/0540_amalgamate.py
59b2de8ca33eeeb0debb658fcb39b4fa8954d6b86a3b48d27699de0f3c3f8f2e  openroot/bin/0541_conftest.py
85cbec1739f67ed2f7525a9873c67c9518d72cf95d00b248b86f510d54bcb566  openroot/bin/0550_test-insert-delete.py
5522ea7aa8dd8aadff121f8147cef88c5a0f95cd5fbd8f3ae647e10611736cd8  openroot/bin/0554_test-ivf.py
5571119fb3e570c5bca09cf91b2ee44f6e20108b6cdbaf91c35cd47df9256a63  openroot/bin/0564_test-afbd.py
fa99917b0e140888dda13cb07bda189fdfad31191d20890498c0d03143bb3f03  openroot/bin/0567_openai-sample.py
1425040ec499a5a7f7087bff1990ba0e0b0c85f781d4aad8258070d2deff4c8f  openroot/bin/0572_knn.py
84ed2bf2c703a854685831a0534ed129369b004b82d55b92cac3943a5b51bb09  openroot/bin/0580_distill-model.py
4cd69e1a36d6547f0ffe08630c9737015ebec45eea1b478a4e00f5079466ce89  openroot/bin/0581_build-base.py
07876cc31ad2991951ffaf4ab710e15b301fe182b23e4b245530295ed526a3e9  openroot/bin/0588_canon.py
02eef6b51a017df8e5103a943bde4c5ed057112363da5a486a49611ead6bddc5  openroot/bin/0593_generate_rmh_report.py
df47e2f074caa8ff65db05e633399535857fa5a1e43026b9fe98477e3f135087  openroot/bin/0594_nomen.py
d1c530d0277b673ee8fc36d96c40f6c85fe2dcc4dabe7d19e3080bfe14567ecb  openroot/bin/0596_thermo_ledger.py
a8855d1de978186cdb788da576b4457576e038ea672ed0cf1fd79d4e0d2e1d5b  openroot/bin/0599_gh_termux_python_primer.py
a4d7d2aa840fc125ac8ff85770501128992f7b60a58323a516d99b0f3a95183c  openroot/bin/0600_justice_module.py
ff8a8fa971d06a273d2279916572f13ec5c7f5bb9320f3b2a2284ea26744ff6e  openroot/bin/0603_extract_seed.py
a0126f89209caf72098491e3dc714b7080c638b9fd18e78114b73592dcee60f2  openroot/bin/0609_esptool.py
90c087b6acaf9bd46f43f325d34b54ee009983cf47f9d0bc034a3a1aa843df25  openroot/bin/0612_Handlers.py
9a035d03d36e80b615edfb1dbdc44abbbccd672f4a05b0802ad4b98366278e96  openroot/bin/0616_LXMessage.py
eeeba0158546d2e9878ca485ffa4b96dd13ce3e71880d784087c1fdae22538d0  openroot/bin/0617_LXStamper.py
4982bea3d03c107c2e0a0c30a2b8186312fc43dedb83bf9ca1fa70806826bd84  openroot/bin/0620_example_receiver.py
df1d50bdee6e4b62016230a77dfcaebf1a98cd8e96f01add8b915a050874a2f6  openroot/bin/0633_fix_bsec_lib.py
f0e0ddb471830043df3126c2a0ff77ba3a8d4df5f5b69ebbdfceb5151e023343  openroot/bin/0656_print_access_denied.py
578dde776ee00f66bc41f78cf96543b18cd2809496cb1bca8898dcabff16f213  openroot/bin/0663_ps.py
1ac788ab499a40a7fcbd516c31e80845ee8757caf7d474b73b82387417eb5d95  openroot/bin/0666_thesis_hash.py
7f789d5ee3c7835bd6b6158d77dee41c43e29cb4421ecca003895e48b0b181ac  openroot/bin/0667_collector.py
44371f9071fef184d4e5f52a1f9325c51df8445270109f3d63a040c5b8bdf110  openroot/bin/0669_make_final_grant.py
51172a6d4cc7e554c4115888337f7288b87ff86f1f360c5f27b48e3f9a1d7d6a  openroot/bin/0673_gen_whitepaper.py
297592fc3835ee0350eaf860df6384af88f3a0419c3931b7b621cfae35ed4aec  openroot/bin/0676_phi_spiral_v9.py
5045d79f48f4e152eff23fa52d0866721caec11a227e0a409b5de80c2b9a2a62  openroot/bin/0677_physics_ledger_v1.py
352fb65f307ca1583968483a6d5f962ad3ad28a6c2714d4be5586fb69a2308fb  openroot/bin/0678_physics_ledger_v2.py
f7feadb76e16e6f6658da219bc8142d8bba77ef4b79d44281274f9deb4277885  openroot/bin/0686__psposix.py
f559161ceedf90cc439e7c376a337b761a732ee0a11aaf2d673feced827e6c14  openroot/bin/0688_test_osx.py
fc7c573443fc8acf5766abc9d27bc6e71e06402bd44aac70d866cb0beb8631f2  openroot/bin/0693_disk_usage.py
23af3f3dbdd21a4ea7aca63a961625ae5f5f6ea2287e4d40a384f27def4f171e  openroot/bin/0694_free.py
671d70288fe0378ab103b8b84c7eb154a367aba05a168fe034d8e87a81a47f07  openroot/bin/0695_ifconfig.py
27bfaf6eee00d5c30d09a5cd6b532f05577798e15d8288bb85cc9753c860cccc  openroot/bin/0696_print_dist.py
93e18c5b1219ea0b78a53f0da9cd8b90253668a6bbc469ccc9707abe27dafe50  openroot/bin/0697_print_downloads.py
b7108ec445d8872cea5809b4ea61714705a759a82bdd87a3e2b6ee5c762b95f6  openroot/bin/0699_winmake.py
2cee887428381768af37a22eda2e6a64e7bbfe8c562d8fb1a3e40071b28624ed  openroot/bin/0703_LearnFromMistakes.py
166c39799f369285925ecbef2b7c26261ac7b3a812410ec1a0b0e4142812c5c6  openroot/bin/0705_earth_loop_v8.py
36a91910358dfee64c366c1bf8ad6d94ebeeda75e81119cefc7f71c898e67beb  openroot/bin/0706_organize.py
5f1dd094619e4e6d9cd1a0c30c573486907ea0ae59d9bbda3a4d4a5af3b62bce  openroot/bin/0707_recruitment_portal.py
6099c51d60643deada69b41d0700f8d1cbfda8e00639e27381f584a4a2e4defa  openroot/bin/0708_thermal_battery_system.py
fa84426d93071ec0d415dbe8d4239701cab4dac71808f15838e2786d11e189d5  openroot/bin/0720_check_broken_links.py
ce704c490bc033a3e10439d040131a46580e0fc7f782309d0d92ffb2d1a79dd3  openroot/bin/0722_convert_readme.py
77a66b645e3d39394bf44f2cec47e22c8bc10ce142fe541fbde158368712b665  openroot/bin/0723_download_wheels_appveyor.py
4732734fdff8ea1a1b1294e6605564d9aab72a6559127ac10e74c3ee0e8a0955  openroot/bin/0727_meminfo.py
256c7406ebae3a96d931a6eb16d97a5e5ef4b234f2aacbd237d081538ba15358  openroot/bin/0728_nettop.py
b30c82f847f0bc813f499258c2563bfee2df3d3fc785b05926f7918d29c9fa53  openroot/bin/0731_create_session_anchor.py
07d40dd5aca973a6632e40f4af9eca389eeeb0e73f0c30d49cdf0e337da97995  openroot/bin/0732_generate_grant_summary.py
dbaf030bf32ac8c0661f42321185ab4ee02638ee595feeb0aaef4b4ed513d181  openroot/bin/0734_bump_metainfo.py
3858ac0d87a8c33d5cf7843e2477f49088d6855f0a95a3194bbfdfc7b74752f0  openroot/bin/0738_mqtt_publish_in_callback.py
a74fc31ef5ed9bccdcb001de01647d6af9df6280ddadf4747e16e661b28ff032  openroot/bin/0743_test_with_server.py
2d428f95791acb79d1c7d4f5bced4e8068cfa2b621016587fac49e27a30389ed  openroot/bin/0749_test_bsd.py
fa09f3272f6673aaf0a2fb685ca609c3f87bd456825e058ba7ce4f3a52f546d1  openroot/bin/0751_test_sunos.py
e1721a99ff842fd553411551e617e0f8c8615bd8cfebe508958e2ab85aaf7471  openroot/bin/0758_fix_errors.py
058d63855de5616a62771891ca4c79f55a1c10f2fb9f1987c9d02ea584753e31  openroot/bin/0761_deploy_v101.py
9cd37e6f274465e18c7c25ffdb2b2cd6f604297dd76532676bf05821d2f5fe81  openroot/bin/0766_axiom_mesh_sync_optiplex.py
f12c6d5f7cc8d80f4eb4b22dd22204ef7357653772250c40b006fa060dadfe4f  openroot/bin/0769_derive_constants.py
8cf830c34798d41a013af43ec2fdec1d470effb0d9e8d0709a75dd9caeca67a1  openroot/bin/0777_seven_symbols_recovery.py
2693929620c6bda63299991ce256624922879aaf44ecdb1144d62a6a3255c3db  openroot/bin/0786_test_tidbit_library.py
a0349a41a6b760eadba8ca6a71cb08bd38e76b30cb40e3657ee5a752aea9d274  openroot/bin/0787_generate_rmh_report.py
d44b140b5b701725a84fb7c78886d09c8b628625ef74d1ce104ea27d3d8633c9  openroot/bin/0789_selftest.py
67ab308c7dcc03b5d2dea5e798c37b40f86a3f77e7a18234790d7c7bdf878001  openroot/bin/0197__musllinux.py
b455365abf996497406e45cb109a3ba9440325a2247dfb7d0ea6a27e210d0fb0  openroot/bin/0200__tokenizer.py
72b021d04dc654656a3e5bba11d445b1a1be63a518ce74d4aa3b8629118fbfa7  openroot/bin/0205_metadata.py
43e05d107556e4aefce46057b7b45c3f8504b1d20a5a8585aa5ac78d1e16579d  openroot/bin/0207_requirements.py
33bf8930a89cdac3f562d57ff1a5bb795181fb1dc00ee282892aec55e09dd94a  openroot/bin/0210_utils.py
bdb4c9d3faee5201b1423944aacaee16688d3d5ca1dadf6afb3c930d3d39df12  openroot/bin/0212___init__.py
51f7921d697c01e4ed6ce04ea070312b874e0ce5a466d7f2fa6fe2edc59d27c7  openroot/bin/0213___init__.py
8c127ccdbecca71e5e6dca85f37c6ba4ef7831a782a4d18755ff5cbc337624b8  openroot/bin/0214___main__.py
c0f1ce9703ac7f3da8a9067a03615c0aee641008fe2689ddce834e1d8150d21f  openroot/bin/0216_api.py
d17a0e8229f534aed0922ee2b240fea12f312b1c3a6d782828481daa90910054  openroot/bin/0217_macos.py
5ef09f925194315c496d78ade758e960c37e94d79270f07cdaa4b50807a994bd  openroot/bin/0220_windows.py
60bb694e7662bb4ee7637a0af677d1e84f58d4504784fe4f5fc82f90959c7da8  openroot/bin/0224_filter.py
c1768ff468e9fe1280767202aa80e447100e40949ce2fdd7ea6731c77cfe4cdb  openroot/bin/0229_regexopt.py
70f07f6bd2d7cf9c6fb116d7d68daac807632dab5925d43f2dce4c70d5fe5fb6  openroot/bin/0236___init__.py
6faae55cfcae88b01dfacfa910f5fb21e8c99e6207d5ea42385a3f98b26b01c9  openroot/bin/0238___init__.py
55a866a438d909df0445ee057d3722f4d1d7bed20e17b76cd3a817d245997e9a  openroot/bin/0241_adapters.py
41f6e67531626738d21cc5e232b7788e809153a45a6ed43dcc870fa1568722eb  openroot/bin/0245_compat.py
7f3e67da77df6bb437d07a3d0270ae35e90ea344b7043212ed59381d095a916b  openroot/bin/0247_exceptions.py
81b9a5b0d4a2f7ab088a0d26aed1f3640653fdf388593a1ef989d6eefe69b4a2  openroot/bin/0252_sessions.py
86ed552fd9db55da6926b5688a356c85195c4517bfbf7763bb7326776b0a65d6  openroot/bin/0263__emoji_codes.py
536af5fe0ff5cd28ec8e251d00449cda200c7378b8ae2fd2f0f60fea4439cf52  openroot/bin/0275__spinners.py
cde9716d3ea83c566736bc163e973592d51e013f957387ee15c4592d018bb4c2  openroot/bin/0277__timer.py
02fb352c76d275cc8ebc339da442d952850b7018987b063be9e341a7ab85061b  openroot/bin/0284_ansi.py
dc74942d50e3eea4245d47455afefc24e8926737f2e72d6791c6219dadbde95d  openroot/bin/0288_color.py
1d45f429c326f5db0a362d757d36e233f876883b65f3248269573195a944ceaf  openroot/bin/0290_columns.py
7c99754c8b519f5f601b0a2ea9383ef333d45b762a401a8696dadf3d0b351fdc  openroot/bin/0296_diagnose.py
e693f729ce5de1027f734285b31adfca18e23d57bb275ccea9215b140cdc57e6  openroot/bin/0298_errors.py
fe2cfd948a5182f5bb30d49e0999cb83e1f0cdb3f81844e0e78dd6a83f1216cd  openroot/bin/0300_filesize.py
432a0aa04ffc21d09baed8921e9f53b1348dc931d8d053b9c2113b8ce4ddf541  openroot/bin/0303_jupyter.py
22dff7f58773ac19bca372cbd24686a2b3c583e05f65601cac18cb8c5a246f1e  openroot/bin/0306_live_render.py
295108ded3b0a3db202b560d4ae1fffccd7f8d45a62d9c11555fca98eb55cf23  openroot/bin/0310_padding.py
974461414fb45154d5f5ed3cc56d416c88f426ad885f20a15f8942d2514dcede  openroot/bin/0317_prompt.py
e611c70c3347724764f22587e7311b8becee215485e616d4da3228e3b47b9531  openroot/bin/0318_protocol.py
e4c64966638d802ea4b9df905befe6d68917c0bd9a47abbacbea54714089cf6f  openroot/bin/0320_repr.py
799367cc6ac8e248bfe78a606373a3d13fb1de5c5d5d3621e3faf20c1db8c015  openroot/bin/0328_styled.py
d63e7eb9f25f9ef940a3942c8bf0026625c39b0317cea826141c8e6d3f7ec896  openroot/bin/0331_terminal_theme.py
00eec93c2cfafa068dd6d8552d73019ed1260cf55816014d1b5a0ceb5fec6a75  openroot/bin/0332_text.py
9fcf88a3c64ad54f85ea3ce583b3da6dce3484b149b1ac04dae34b287f70ee25  openroot/bin/0339__re.py
76c89f152db161fd62efa9a64727f3f72d76e710bb67f1d0f38e592a126c617b  openroot/bin/0342__writer.py
0982425790537edb5961fa98de6a2f74c044fbc6b3eee8444ff2d86ca4f6367e  openroot/bin/0344__api.py
9d994b90e9accd413483aaf2470055198e423b33f2b9d72c889b4359aacce4b4  openroot/bin/0345__macos.py
52f57b52ab464d229dbf0f0dfcbc56b848a464b9b9801d7315f4d9607f4a8409  openroot/bin/0351__collections.py
1427fb5142d291fd7472e4d15164d0112cf1825d564fc7b6682cb791fc998a7b  openroot/bin/0357_fields.py
781d9e59fbbc5b3d5f9feaafaffa84fdd64071e724d8d72fed7435e4396f55b5  openroot/bin/0362_socks.py
b1e3fcf90e41e9b07474cb703e3f98719650df4bc7b8ba91bbeb48d096767f3b  openroot/bin/0368_proxy.py
63d44d9160887a10f1211bf21671d48e23253e8966dfaf0660cc9ad9874339a8  openroot/bin/0372_ssl_.py
3c40d0332a6276e75ed2701972d2cb8852bd7a937e2cf9d21fb2a938b2f0a87d  openroot/bin/0376_url.py
8f795b64ad633f28b00f7e13f08809cdd5846554fee04fb4bd82098bd52378d0  openroot/bin/0377_util.py
08d7903e7a40b9d63bee79b33a438d4a6020465cc87f4e97f97f66bd160e0e6b  openroot/bin/0385_abstract.py
293c019a75e56a8a498500ce7a6547607b24883821baafb4f18b4feb13cd24f8  openroot/bin/0392___init__.py
fc9c745d1883ff9f296a5b169f22eb2ee879f59a4608f20f5cb29d668f4e26f4  openroot/bin/0399___init__.py
9630d0064bc1b42f314e339d6faac3273254362d6cf8f9d547f5b90be32ad039  openroot/bin/0410_main.py
623cc9023a9fefc01136c2e59c94fd97a7cd6e9c833c903e6ab3885d8b0ae489  openroot/bin/0411_main_parser.py
12f04bb118dc4d132b3aec8790b9494ba5ce0cb05b6ac365bd5cdc7bb71b46fa  openroot/bin/0422_debug.py
073dcb7233505e4cf80aefffa4be0267cea8e3e1cd2d98f535959d949863baed  openroot/bin/0426_help.py
2e6cbbf961d9ee3b87a7eb718caed4ef85f78ebe5c7ef80e303202c8a8adae23  openroot/bin/0428_inspect.py
9d72643a384bcbe3b616caca53d448a823aa818d8fb28296c9bb598e3460a94d  openroot/bin/0444_sources.py
88ff725599ffe223ee35c694361d80fef24b72f519fbccb8cef28b0d512a68cd  openroot/bin/0445___init__.py
0089a36095b13ad0e473428a73a6381b3ebbedc83dd5c68c0382fde01f456448  openroot/bin/0448_base.py
5383255d6141fbc7afff285eb8c3bd4f69bfcb96f80be84ecd56a81d5a1b977f  openroot/bin/0458_installation_report.py
df5261f991ec4c80592defbbb8f36860b8914965c08c42358c6371c2a2ca7780  openroot/bin/0460_release_control.py
d2d79e930495c56e4c3a4d163c6e4da2fc39abf5c98f18a371def99193ba13d8  openroot/bin/0463_selection_prefs.py
ffe467937bce7dff2e17d8401a64fa48b00b7e563580c05c6c6c12d767dbfd8e  openroot/bin/0473_xmlrpc.py
1b1eabe7b2c6fe0baf0181aa29476effaf2b1cf3e43bb090fea736c0a9d8cacb  openroot/bin/0476_prepare.py
11781b314700b4168d8fa7189acd19c1e23134e4a838f7101bc12a5e5f476213  openroot/bin/0478_constructors.py
89d563e2e55df32408050a23a2e94bd5c7971abd5093ca27817cf0238bd34ecb  openroot/bin/0481_req_file.py
555ccef14229e93394fd0084a12c587641b7f73e78a4a3d08e0f19eb3e166cd3  openroot/bin/0482_req_install.py
6b092a2179d80383eb9ac8f441bdf386a75b61499777ed68d0ff8a6779af450b  openroot/bin/0483_req_set.py
fa31cb384fd31da673e4115c0a7a122fd11802d2749d77a6e3db3da1fe23bcac  openroot/bin/0487__log.py
2ebcc33d930a561d2bb9bb42c7dbeedd79596cb092ba0e954a3e10b2fb7ae810  openroot/bin/0488_appdirs.py
0bd2c75c900a930007f079f79cf933f4460adeba8f05e3bf21790e1b6cf3b1d4  openroot/bin/0489_compat.py
b0431adfca9aaa3bf1d5989ddce0805236b7d4138153e512b9230f06f537ca3a  openroot/bin/0497_filetypes.py
0fd73c0fb58e3eba0e3bc1860eaa417954a3d74346166ba71b4a364e87638c85  openroot/bin/0506_temp_dir.py
a86f5d269e289e4eac5c8f1a7533743cc4d28fe9238c60ad3599f35ac20c5548  openroot/bin/0507_unpacking.py
61d46e8fa322706f90f4c834dc56d4bf55932da9ba2dcec08228d8e2fa15ca2b  openroot/bin/0510_wheel.py
c3564958b2aa34fd689c48e47e39700559cca8f64d488111f1aca341c9d3ab8c  openroot/bin/0514_mercurial.py
b9481d3efc66bc407c430b63af41dcd178058db88d8b971bbc8e2f0112ce257a  openroot/bin/0515_subversion.py
f1b6580c264b5d274b1f2fecd68e5fe2bd791e62afa85521cc1510385db52ebe  openroot/bin/0521_found_candidates.py
b440bb305f08a865385b0f6deb56157cd14ab68690a5bebe0302d9a6d273d551  openroot/bin/0523_reporter.py
23397d9fc9dcd7cf250350523d2f10c5fb9d7c340f1e09e0c3e8a3ea15edd274  openroot/bin/0524_requirements.py
6a4f941137103ca94565a5a860a5aee505576e9141be0d2c5dcde2d0ee2f4986  openroot/bin/0526___init__.py
8d4522768c671dc7c84c71da0161b51b68b97dd058925bffb89723a36c7b5581  openroot/bin/0528___init__.py
b27795878ffa5b14192b8963765df2955b8ffaad2db52a9b825f665add079ce8  openroot/bin/0529__compat.py
b06c31a8702d7c0a45dedeaf48b89871f3e1ee6481f0fe8b6941ed9c3c12049a  openroot/bin/0534_feed_oracle.py
8254fc117ad9ad714bd436003154eaa9c7c3ce8cf3f882985faaf2963b5afb3c  openroot/bin/0565_build.py
094250065825c232d1d5d465be5fea0486b18f6a21424f9aa58794f797f1e9e6  openroot/bin/0535_generate_system_map.py
126ec9163828af22068c4e098cea2af74a51904f2575ff23ef2d19b0eb39ea99  openroot/bin/0545_skip.test-correctness.py
32bfaf5d02f18abe979f0115a0bbb7a234d90f0813f3a780383252f8f39d2285  openroot/bin/0551_test-ivf-mutations.py
605d75207ebd1c45fc5f0e0d5936cbe7bcfb112294f8b959b5038cb77abf823e  openroot/bin/0552_test-ivf-quantization.py
7fb1502c7881d4788aef5b0429c56ca4d9040a1be0b11e6e6beb4c1c8aa3be94  openroot/bin/0555_test-knn-distance-constraints.py
7b0fde7d757e502936f18940f1cacb06523ec823fdc0e31937002a249235ada2  openroot/bin/0559_test-partition-keys.py
14c331b483e035f5f5b1a4c04e40206580999f2f8e7ae7a814e0dd26abd1a0bf  openroot/bin/0562_test-rescore.py
bfc4f8b9c9ae1ec60d8628027634e9e19e0b138fdbe09870f35bd8ece1c1da05  openroot/bin/0569_extra_init.py
bb540f123f472ebcf2b9974d7f2d268eb3b2da3c4c8a0110f2ee50d64d762982  openroot/bin/0570_bench.py
c7e97041343d782b9972f79c39b424d8702682b28b7ad2844ea4548bef02b505  openroot/bin/0571_build.py
be8f285a52529905bfcc6c9bdbfc419a0f3bc3f00f069ba86a6864244fc3bc0c  openroot/bin/0573_test.py
653d94ef309ab65cdbc42757e4a6f3b56c8159fcf115aa35d2c989c030b9eb7c  openroot/bin/0576_build_base_db.py
36f15b84d2c609888555a87a779deca41575e60da5c9cf0ccebc541afc1119e6  openroot/bin/0582_build-contents.py
31a8010702825bf1fae9673bec6cb56f69b4ecbeba53a29ff33c4147f53a3d3c  openroot/bin/0598_generate_rmh_report.py
27de69e036db774d807600348496ce898ca871ac7cec392ff3fa4cbb6ca752d1  openroot/bin/0604_fusion_core.py
8373758a63f415b919054431c95f579bb414030129ad63fc06c4809802ebda6b  openroot/bin/0607_Example.py
4f630ac89fd19f25412d71988bea504d329cde4c58b75e32f46d4fc83b5767df  openroot/bin/0608_RNode.py
65638375cf755684e681179fe00743cc4a80a04213e2ca16ad1caf32a54277a1  openroot/bin/0610_gen_esp32part.py
f70618aa50978de8115c2308c905c230bf80a17987b38806e0942f361a31bcf3  openroot/bin/0611_spiffsgen.py
23b280e47f0690d27dfe469c3117f9928363716260dc85c9266f5d91146b8e90  openroot/bin/0613_LXMF.py
9439444641247cd5da8cc4b5c980a40a2584ad82b2cc0666daa5280f1632dacd  openroot/bin/0615_LXMRouter.py
03d60f351b9c23f79d69c42463d98b5a4796d7840624cf2f71c02a6bf648eeb1  openroot/bin/0618___init__.py
8aa3696376baae4a4d9135fcdab3f81f92203275516b60c3ac1b269529851ef2  openroot/bin/0622_lxmd.py
16d6d263d6e86f1721d2bb39629bee126e4f2562a7790e7af33e49c1c1a0426d  openroot/bin/0625_test_classifier.py
e30630c1026b251429abf69c593a2729a6e0679f0636c1cfa05151e4d5012772  openroot/bin/0626_kernel_translator.py
6def360b36214072f626b502bdf8e76998e16905bf7e1f6eb1fed07c9ca40e12  openroot/bin/0628_fractak_swarm_engine.py
c51a2e3e2c133aea1c80cf6dfeda141414b37072d7a03eda5c9a03ce99458e95  openroot/bin/0631_setup.py
9b13acb75568facffb69e7423a4d176a141300c516c10692f28fb4a1b0287cd8  openroot/bin/0632_conf.py
ac256f8c537d1b9d32c0d69360ee8228be1d2ef831308c0101ab982b14de9f7d  openroot/bin/0637_disable_adafruit_usb.py
bee98fcc3449775cc7863ba2990ed45d95209c8b1de6b5beec337aadb5408af4  openroot/bin/0640_ld_response_file.py
bcfb997e439e37505c36b61e65d6ea0f90ad1a78a14fb60d2b18b211ece969e5  openroot/bin/0644_wasm_link_flags.py
9859d21860bf8b8878aaed86768cf632fdd2c354ebdb8a1bcf0a43309711db83  openroot/bin/0646_testsuite.py
4791f1c8b32e829bb1c9743161f40797d67e3cffc0834292488d01017fbf4e99  openroot/bin/0649_test_linux.py
a4eae32bec23a1d89430219b8cc0ed4e99e8c6a818e36343d4b1cc121a4ba4d3  openroot/bin/0652_test_windows.py
dba758fac4044bd3c716fcb31544abfef66bd49f911e2722e648b0c1d8dfbddf  openroot/bin/0670_aerocement_triad_v1.py
0f71b1ef50239e664cace9db6dfd014bb00b702e3175c5c3208cc0e4d74c5c18  openroot/bin/0674_generate_thesis.py
dc18da013c5cba1dbe0f49dfbf9031d1f442d57ffba7cdd9f6cf1dc0637c6ebf  openroot/bin/0679_thermal_battery_check.py
fb13e2b48f64029a76b59644b019336ac5adea3ba10d0a113e79de13e2c32f95  openroot/bin/0681_test_full_integration.py
a6cea19d7b0cc0e7894e6a02aef11afa8159c45591034ffbb65e3bb11f974870  openroot/bin/0683__psbsd.py
3818f4d55ddfe7288d82fadacbe31ff50f00e4ccaa352932b118bf02d33d861f  openroot/bin/0685__psosx.py
cde80aa79e5c5db11c6a2313bb378319e85c66af44c943032856a6ac7f1cf24e  openroot/bin/0692_test_unicode.py
4399a812f430c41d061ec12d1d856c8b0e4f1bbcafcbc7ca83febbdd566e5abb  openroot/bin/0702_who.py
f653d2ebc116c9dd5fafe423e5707f936896772ee192a293f1ab0f284fa645b8  openroot/bin/0711_test_acre_workflow.py
bda85e6d37e7bb72908b0b53b17ab304cbd17d0ae39e57ef831161ed795eb2cd  openroot/bin/0713__pswindows.py
7d3ebcf4baa9b2dc4f125898c0636b062c5bfcd82ac8afe2e42d3adb4e9308b0  openroot/bin/0716_battery.py
4cd50e3b76f9cd38f526ba59c041930a9afc1b0431a431bbc8010e8daadcdb6b  openroot/bin/0717_cpu_distribution.py
285041b5cdea676fb648b73d145d030f34507c2da4804ec8ae23bd8737264e3a  openroot/bin/0718_fans.py
1f41ecefffb36b6cdb9dc9e4b1d51b5639bec84be2575642fbd7cc9806f2b34b  openroot/bin/0721_clinter.py
ab2ffca7e489732653b0d82b694e72cddecad39a43ce9505a12174c8db6d857c  openroot/bin/0733_unified_breath_loop_v3.py
f910a58a3f548a0331760522edaa83829164252082aab5a1b1e931ee6e49c850  openroot/bin/0736_stm32_extra.py
8d8f6e58f855ef4a22a66b01b8efedd1d61dc46790d3662d10a8bb4aead68e5f  openroot/bin/0741_test_interactive.py
e1f70baa7c17962dc129e394585d5f3eb2c7023b04ab03a0f73e98e4030542e5  openroot/bin/0744_verify_system.py
7739f16fb1675838b82f562412dfb3b61cc0fd4e199e5cf80683aaeb13266321  openroot/bin/0745__common.py
7b39b57496ee8a638b118464ffc2eb012d5117e8464f52a485afe16fcef6d2d6  openroot/bin/0747_runner.py
aa42d79e4555604a8cd88861203d02cc45560260f821bee2d04e26523a3c27f6  openroot/bin/0750_test_process_all.py
7ce08ce39f2f19d1783bfa7eb5c5ad59d14cfb465a91d791fe1fdc7c13e577f2  openroot/bin/0753_killall.py
62cc5ec444f68c1ad03f9a5649c33d61805f31cd976e1263fd2e8d31917ad729  openroot/bin/0765_rmh_labyrinth_model.py
98fc5fe02d66255527ca1960a27d1d0cfd0b29211246993cc8d195cc535322da  openroot/bin/0768_agape_cooperation_theorem.py
51cb379a1942918918342af3caab67608785910d57dbb059e3de67fe2f2a89f4  openroot/bin/0775_sacred_language_theorem.py
d85fe70db8bac08608485d30e367e4f8b4a68acc99f760a9234f313e3c4cfa35  openroot/bin/0781_theorem_generator_batch4.py
678aeca72f5875307535c8512a25ae0d578ccb180aa094259ed04c57058a75f3  openroot/bin/0790___init__.py
f686d9759cd91819c9f1c5c53e3dd3bab6b8d59c86ca47c57a7be27b8895bd95  openroot/bin/0791_solar.py
85a960ef139c4e1423e5197c1cf663915be33f988e63fe8238584b0510be834c  openroot/bin/0796_agape_board_advisor.py
faa61e8d8289488a0db9a380e84c37d5ca919f636e734eabbc4f78ee5f8ce604  openroot/bin/0701_temperatures.py
cca2fcc7fcf9d4aea0a17a25d7931954e1792a8dfe9bb71717f573a795bee21e  openroot/bin/0709_data_logger_example.py
df939f2d0d00cbf7fc2401118b27000b8021b97abb0d2b8c929b44edd80eb331  openroot/bin/0724_download_wheels_github.py
a832806637a282651d10330cea13b7190c265c185c3b49752d02f231dbd7d225  openroot/bin/0739_quick_test.py
f600ae45fadd3d35c840fb548224728df977b4ad7bdd4be55d75183ea0234303  openroot/bin/0740_test_comprehensive.py
1620e8c4b69d7a1e20c5e2699f108db297c50ae02e30360b85dc5c438ef0ea92  openroot/bin/0760_ai_bridge.py
1d3ebf81a993b082eba26683fc0f189102a5161db1067d1b386e28ffc2e2f430  openroot/bin/0762_generate_rmh_report.py
6b165df9669ba5244c0e37e0233035c732a5ab8d95e71ae8d8ffa6f2a00ace29  openroot/bin/0770_energy_theorems.py
9d048c003806c6529468385fbd67222c66131c816dd73fa5ca1220bb95c90db1  openroot/bin/0773_proof_builder.py
38cb53a56a88adc3e42b9efd760e7dabd62166eba073a64cea620e9aa0ef772b  openroot/bin/0776_sacred_merkle_system.py
f51b15f6fa621c9492a52907614d4dadbc0c1fe44c31709992b45456193e9a42  openroot/bin/0793_setup.py
d083405bc7647d964f4406aff463527721a9272931fac3e8c34f05ab75b6455d  openroot/bin/0809_Minimal.py
ea6741a67cccbdf0a85a8eb42408ac5fe056deb10a533e3db25de4abb3111f1a  openroot/bin/0817_Packet.py
4c72ece9e6a885972c72ec7e4e0caa7cc810915d4dcac872993b17f6d1cc0436  openroot/bin/0818_Resolver.py
fca313646cbee51979afe530d2151df1652c6599eb9fea236064581a9edc34f5  openroot/bin/0831_AES.py
8c2f200fe08566f7cf1adf078cd8c03726622fac55b677c081f3e7c0e735472f  openroot/bin/0836_PKCS7.py
1798cf2bef6e16ee4e4123883b8ec244fb696782b7f662d86558d48f48392ea8  openroot/bin/0857_WeaveInterface.py
b23a844b965a9f2c0348561f92ace63b6d85e59f371ac58f39db993e3a556d71  openroot/bin/0858___init__.py
5ceb68f1e0217d10b6ed2233be73ea3ad52909b16cc3b1ce1246419be7118e26  openroot/bin/0862_rnir.py
cb63bcefb7a2074fb0333c276310fa57d78c26e5ce530c1df1730d2da045f59e  openroot/bin/0869_rnx.py
1421f139c002ed0fb1f92d00c48308509356c82dc5967599d904ac882f82eafd  openroot/bin/0886_highlight.py
5773626def2015feb42da16bace48a3d22ca1fb56104c86f11ba951cacead85c  openroot/bin/0898_loop.py
fdbe578b9ff7e0440ed7b6f2607c27a7cc1483e8a92546610301321b9f440d99  openroot/bin/0901_retry.py
81212993f43c217bd16294cbf8d4eec49e6cbe39bd549b48665b3cca3771ac22  openroot/bin/0907___init__.py
a744ae50514a28411135f9644f31813baca1135d6bd11fdfa5f025c813d26d99  openroot/bin/0908_netinfo.py
a99fdefe6354c28c52eeac9c1e851041b69dad25b8a3b521d4f57b761517c798  openroot/bin/0935_libc-util.py
c0d9718de758d5729cef3def36cf9fa2c853b53cffd28fc2471ae694db04ba77  openroot/bin/0936_unicode.py
b8602d1c3fc3237a74c2cf33484c592de64cf83b37740bb10647639a4df07641  openroot/bin/0949_ggml_to_pt.py
4742eaa040e0657fa1247a1361e0d856c62317a43326ea59a40c2e9edd8d2c38  openroot/bin/0955_basic.py
93d61155fea4a19a9bb6d056dfac5259a26959d6706bec50554f401c4a3d0ee2  openroot/bin/0969__connection.py
4729cbb112941062342a2997c9d943d5f6447c4cd6c03a345289f7cce2a11b54  openroot/bin/0990___init__.py
9cad6292b75254af606a970aae9bff6e5ae9f0b08089cd63acafa391b60794d2  openroot/bin/0994___init__.py
a353faec53162101befd17c6b4a8ac9641f0a38a579bfea37ec478d4ff3cbfbf  openroot/bin/1011_config.py
6f15bb7f1ce054c01d3536f04f4567ab4e202435b5fe023f1858903ee3328cbd  openroot/bin/1047__exceptions.py
0a0f4631a6e24d3fecc1a0df5202118ad4b0c4b44c4b05033a6ecb7521aa940e  openroot/bin/1048__main.py
25069c6a3ba112b956602a620daeecfe22b8ac756e6b7e8cf8491a189fcf9ab5  openroot/bin/1063__models.py
17e127a6cb9f8ccbfaa0bd3d78003cb3889a4f90e1fdfaa254316039ed2bc1d5  openroot/bin/1068__types.py
e4230a19024b4b37b8f1615739ea8fd3c8702714f24ed46e06e5efd1b716cbf5  openroot/bin/1074__logs.py
870e3dad4afcc4a08ab3b465f3ce3a6d4cd3e89aad2a5d9d159a2663c13f8a52  openroot/bin/1093_batch_list_response.py
e08a625cc28cf40b93ca8a793d1a6d3c16c1861f6cf77c72daf8e0e18c3a348c  openroot/bin/1119_chat_completion_content_part_text_param.py
18d1f32858bd5fb8bfde8b8296036bd048f41f6bcbc787b22df5f32bf086bc06  openroot/bin/1136_error_object.py
4d06e1d04ac40a54b7b2f832b32abd73a24f1a7ba49cd638b0c970671dcca92d  openroot/bin/1145_transcriptions.py
9194bf54c6d58987c5e7bd29a205022756ee973fb26df2f9d4faacf7292d79b5  openroot/bin/1152_base.py
03379a454c95c0271c4f2c8d25ec437f49f57457f3cf2769748420bf0ecf2e79  openroot/bin/1153_default.py
35c3d7dd76a9fc4c0215958efce692c9036e227098c7540c35b3bc1807a2ea36  openroot/bin/1155_wsgi.py
473cacd49a1f7e7e097331257180eab192d18018079f69585aa0d1e79a0048f0  openroot/bin/1156__config.py
24bc7f3152dea7b331975cdba5d3598ef1c3733f89dce116e9671d575f3875c3  openroot/bin/1162__discriminated_union.py
36b9bda054595a9f3e8e57ef3e02482c4b32c29e18cd90f9d972063c32f11dc2  openroot/bin/1190_tools.py
50b39a21481850306c1cbec411511aadc33e52e6ca52082837c8526c3a27b051  openroot/bin/1201_class_validators.py
8990012d8a7a395a28d801643fd229ae2ff049cebe2a496ef18ba149aaed7798  openroot/bin/1202_color.py
bd10754dba64ccf3773f98a326573e72336e3be1dc88d3a90b86fc2b7cd99df7  openroot/bin/1213_main.py
db3564ae5bfe0ecfab5866aa69796b84426201014fa36dc14f71aafec5a80575  openroot/bin/1229_http_proxy.py
031538ca172aebc067e6fa9d258b625ca6148fb9ef8586f1cf7bf8ad3e319ef0  openroot/bin/1242_http2.py
b275ce378daf5031cee49049be8f03e155a4d966ade38cf63975c70eb8db97de  openroot/bin/1244_interfaces.py
35b994e4ee545f7c44c800a7926617dbc166c1d97e7fe9f2d2d1f29b6e9ed30d  openroot/bin/1253__resources.py
8e7da721b4d19410145cbfa6c7f6b723f5676ac17c19b545a41469dbe6300b1d  openroot/bin/1258__synchronization.py
9ac9eba2d54a18c428994bbf463daacfd32f21d529e9ddc91abecc3843bc915e  openroot/bin/1272_file.py
16bb80272fc6ae98c07c72e96f873721519fcb65e28bc6f50479c88f151f6db2  openroot/bin/1285__psbsd.py
5fdadded61ca43a994027da285bd373029f3ac1b50b2b3d1902a2e1319ae6a04  openroot/bin/1288__psposix.py
66c9497bbebb5690aaebc0893e4a6d0109ef48843be3117ba98587d59e912550  openroot/bin/1291_battery.py
8b71d3f84c28ab156efa7b8829d17785ce333b287456d8bce14e8db700254873  openroot/bin/1297_iotop.py
36095743837e5fda6ad8ddb4a562ab3692b3bcb73aad0b4476200f2542f8e879  openroot/bin/1301_nettop.py
3894ed6804fdb21fe88234fe1f05c08acbaf16fba84de34c41992adba8af2a56  openroot/bin/1306_ps.py
3fb56f8acfe360133ce38da6313ad5aa29439b34827099135025df6b8f6a6ce1  openroot/bin/1307_pstree.py
3ed4fc4374e57ad2dd20987ad71b94b42aa22e39eab3b1226b5c38f5eafd96f3  openroot/bin/1317_convert_readme.py
9431b4f0b64d912b68225bd4ba535907773aa8387ed7204139e19334c14a6f50  openroot/bin/1325_print_dist.py
0872fae6ad886316fc12bb4901487ced1c8a48259ec309808385452bcd1aacef  openroot/bin/1336_test_connections.py
2cfbe110f50f490e0c7710650113dc4784e1b1dff036a2a4aa3d09aa52a4642a  openroot/bin/1338_test_linux.py
04a46a3f17158ac84c6f14741f42c8c2ae831fa23d820998b52f9d06588ef6df  openroot/bin/recovery_final_status.sh
5d850fa5b7082cabc6fcdb9d631fcf3104645eb4faf87df7d8fd09ea83f85c72  openroot/bin/cicd_quarantine_seal_v1.sh
7c3821465403050063a9e375f2ae5eb4b8d1a49832e83e058f6292131f2b4f1c  openroot/bin/0824_clean_md.py
71082bbfa857bb243bf2f7f9203c61a55a43f39ec8059e4b33956625df4ba01c  openroot/bin/0828_identity.py
734616536bd408636918fa700386ef4c375354883b7f9a47d166804e13397b54  openroot/bin/0843___init__.py
a60397cc731de0e7d7392aa3dbbddd301214872a5dd3a27f788219b1a1266be4  openroot/bin/0856_UDPInterface.py
ac3e3dc2815f46dd9251a4f5f6bbeb1afe15ed073b7623a10c9b18f5f3317113  openroot/bin/0866_rnprobe.py
c093046cb7151bda809fdd442ec4bc5babef0e4d26ed95bd7f8256811fe9526a  openroot/bin/0878_exceptions.py
8c724096d97ee14ac1a4ea1c5603147ff7ff9a80f562eab5ca810461467a8a4a  openroot/bin/0879_log.py
fe657eed076ca3657fc2fcb9a235084eaa36b9621113b2ea0136d9a05cc453af  openroot/bin/0883___init__.py
c282a8a1367cce54394f1b36af4eafdda26987c24acd42e12f66059831c11227  openroot/bin/0894_exception.py
f30dd353d3fa400bc2db06ab48ef545a610eee6cf055c0726bf63b609dd298b3  openroot/bin/0899_process.py
3c40154b25843df7e746bde9fd1e947d2188bfe997d9f9a6277b3374e8e84013  openroot/bin/0903_session.py
cc5a600287831e81a671a0f536f60a091ce6b29e694ec65f39755ca93420ad6a  openroot/bin/0905_RNodeInterface.py
1e80d0250eceb97c344c965bcbd44abdad184a31cf62094ec8c2a3c53cb646fd  openroot/bin/0919_bridge.py
4a20bd8f0ef2e72a1c3cff153a6d5f9376f9abdf0fda57032271cbb728a192f4  openroot/bin/0922_glossary_linker.py
e488f0a396650249924f5e4c4c58249be81f371d7276ae5774a9e6c1dcc383b2  openroot/bin/0924_runner.py
a8b368ba3eec1a16eb3d3abd3317018a8a393824937ec381c0b7f85c8e283d17  openroot/bin/0926_unicode.py
f69815fc29eb60ea56e67c869ede7eceb977a863f2bfb892b90a29e411dc1ec6  openroot/bin/0928_gperf_fold_key_conv.py
da9d198544d89439c3b4decb1d2a9952ea01dc02cfe1fbea4f4d20aa573a7d7c  openroot/bin/0931_make_unicode_fold_data.py
e16c4a685517194a126db981a6745977e9f78768ddd5c08be2629746e2bac7d6  openroot/bin/0934_unicode.py
d49e26d0b8b2b201d00f2f46bf1f9db46f873c27332da679c9a7adbbf54462d2  openroot/bin/0938_walk.py
5593108b5cf0ee7a68f70815577a5e2133f37a134c74f4e85aa1e27adbb71f29  openroot/bin/0939_create_text_files.py
0862d1d1065cd3347d7c6615ffb7b4dfdd1ffc5b0943477cbb8f8c5f4b7bc2ab  openroot/bin/0943_convert-parakeet-to-ggml.py
f562442655eeef296e3f462d239490f4cf4e4d07db34791a75aacad6f5c60cf3  openroot/bin/0964___init__.py
3fb0fe9413711f074b64f2e29a6630acf1bef59923125bef25925d6408123fee  openroot/bin/0971__headers.py
58fb69a477c8daab359e89338e7f1e94bf0bbf2a88d3900ae59b25865a3bd40e  openroot/bin/0985_lowlevel.py
a5a32923f54c3507f66e2af42dfbe03295d28982681c3cd674a5154f2a079af4  openroot/bin/0986_pytest_plugin.py
ba7666783b1c8415821823c2c244b75a8b7d7ae2ba6e0fe42b12ed193c70db5e  openroot/bin/0997__api.py
724e99a08cd84e474d0087eae4c19e2aa0570edaa3397faa7d8c266456eb19ca  openroot/bin/1002__trace.py
8bf5778fe3d87462d22e68ff20965e913463ba73bc488573f0b325aae3f23fb1  openroot/bin/1009_class_validators.py
6bc66125f23c143e934030fbf9c58c9b5657950bdad3031d4f6132e55bd57be3  openroot/bin/1018_fields.py
75ade143dbd03cb1213ecac39d49628df4357ee0825621959d4cceac064b803b  openroot/bin/1023_json_schema.py
c2477cd9d82dbd6b43f3de54fc8e84d61b6a3251a1052604577f5cb8149ea370  openroot/bin/1027_parse.py
56aaa3beafcb9daa5592779b51ddc1a7f275a768176599d94602f8f1b5441bba  openroot/bin/1029_schema.py
7e961c1a702770ae108da166de366da98c31258cc1eeb2493df025f3d7a6cf24  openroot/bin/1032_types.py
4f9af38b00cfacc8df694d17fbee5f05d195be1f784339cd43b4230f82df8260  openroot/bin/1037_version.py
a4fa7653ec2271f70ab05f8a6111352d876dddee84446788a1767c1a3a372d67  openroot/bin/1044__config.py
28e1c465997aa28860f663da2b2caedf8e6aab5ac92e0df94d41b7600cd70776  openroot/bin/1050__multipart.py
0d89fedae7c180c797cb9b3cc77fd307bc2302e00031ec136a43eb9b9ad712c7  openroot/bin/1051__status_codes.py
37fe4f3ee14db1aca06ed03f9e965df7c4953752d042f15328be9b9163c16465  openroot/bin/1082__typing.py
63932dc9dfd9d15bafb3ed69e71a09994d9aa6082958dccb13eeee64cdace418  openroot/bin/1084___init__.py
a9d23b13a4722a075f73217735beebc1ac5c513cd16907e5a654429379d05c68  openroot/bin/1086_embeddings.py
63ecb7ab702f2877bf7d9b93ca5bdfc10bd40da27521434d015a41749bd2c2ed  openroot/bin/1099_file_create_params.py
f7600ed1af68dde6d4aad93aa87b92a830acd1feb858071716e688501caf330f  openroot/bin/1103_file_list_response.py
0e5bbd60ca3471ce38352080b4b7d99c4ba090ced5040eb3c36bfd6dfacb321d  openroot/bin/1111_translation.py
48a440f6a3fc4825b4a11b035284e6460bbf47533cf08b1fca865951f56d831f  openroot/bin/1126_chat_completion_named_tool_choice_param.py
d3cf9fda67b17bc4f8373b1febba953ad53a4e66a8d2920d18d21adc096aba3d  openroot/bin/1128_chat_completion_system_message_param.py
851f5d4f584b07b507e89f4d6de9f4f38ff2703dad3cf19b64a40fb5d7fdd1f6  openroot/bin/1149_completions.py
63f836b778bbba5b8afb05c266fcc97d114c3d4336dda0582df69ee05cc13f2d  openroot/bin/1157__core_metadata.py
6085af4a6011e5f9db19258239076e5add72078650638d9e02bb9cf9e9eb6fa7  openroot/bin/1178__serializers.py
9f48d840e71be58422c346fb617ca2ecd3e261d57bba3591e0ac99ba68d33e89  openroot/bin/1184_class_validators.py
4b140f925801b385c727013a059f6aa1ec18a0688dc98527987cc414265b7e72  openroot/bin/1198___init__.py
ba4d8d000c6a88d10b2a388787287129a20e87c1759585bf2f3ad6dd7ee86417  openroot/bin/1200_annotated_types.py
cda6b1c71a163c29bcd7c0f56ecd3285aa518d79b7d95f06d191d609d335b970  openroot/bin/1206_decorator.py
590e47cbf848a5f751dd84bc93a37613a28c273b1d6c18bf95d58e3c9695f353  openroot/bin/1212_json.py
1d836d2807ce98e9ca269b0383583a488923f563e153ffa2f25e5ed89281a46e  openroot/bin/1215_networks.py
94b2a02e58203df84596a8b438378190e5afb7d0a0841054caab27b14d6dc7a4  openroot/bin/1231_socks_proxy.py
69286045d6673264611561deb63ba694cef77fc2b3d58380c8250fff8907b250  openroot/bin/1234_base.py
8477f25746d70cbf91d99367227c2c7b79e64c0777e80233d5c071826030cc04  openroot/bin/1252__fileio.py
9a34c107685328d3d1954d088678a379079da563861110e23234a5250b05aee8  openroot/bin/1254__signals.py
f45538db78f9d970417c656be8c7733d3772c3c6c6af30296799b7dfcf80b6c6  openroot/bin/1255__sockets.py
4b39d8200f24625158067d0465a9fe4986160ed041021b139d74c74a3098f544  openroot/bin/1305_procsmem.py
bbeb60bee7b28f837414c5516d760b65db2cbc36ede7b9d79ac9d5825c3b1e21  openroot/bin/1310_top.py
1e38d2e351113b7c6f649e6d0885ace3fc4851a35fbe5a49c4ff577f70c238a6  openroot/bin/1328_print_timeline.py
7f5618e9265e6dcb5de47c1bd629f8d2715285f270e3303614b89db1d83f798f  openroot/bin/1332___main__.py
adfcc63ff66e307c73b93cf70ae5719fcfb35cd7b9ffd6029b5679253297a93f  openroot/bin/1345_test_system.py
9816ec4416d47f85660eb2936ef952795aa8ff91d333d87879313f559ff97977  openroot/bin/1346_test_testutils.py
e169e8f6f177d8627ee44d141402aa121e47ffed34611bde5880874a32299271  openroot/bin/agape_ledger_chain.py
43ce55ac52b28c34b0a4f9f535ec50f96ba27209bd0209ba6a3188b3c9a0431f  openroot/bin/enable_vector_embeddings.py
008a6d7b45c86829fc1ebdede81739b80dff552983d46bcf02e475f156253f1a  openroot/bin/rollout_openroot.sh
145c54d53abf573b5c572de074ef0abd76c6b4cb686072cc5571eb6ff7a894df  openroot/bin/hive.sh
176a3af750608e23533bb92860a3aa323ff36672ef0eec7f3a7e98f575cf0dd8  openroot/bin/thermal_frontier_v2_water.py
c20733859677db75961bd5f724f5bcf0feae3cdd965b0fda7fbffe70aa778a52  openroot/bin/0804_Echo.py
f452485868f3d8f561b8c2eccc704d1759a41e1b2edd9f86490eb1694e05c88c  openroot/bin/0813_Speedtest.py
3b61230665fcb682b40fb004dc970a0a79dc4fd9c47fadb79ccef163a7723f64  openroot/bin/0815_Channel.py
aa39e02a68dcc0a9f573f070028b9575a8be4db9ee299a39e846ea45d20bc5a2  openroot/bin/0823__version.py
a153b91a33bad236b31840e279e578a7dafd7c773f11ac7b2e6a44a952c6a9d7  openroot/bin/0850_LocalInterface.py
a21b551e30b6a0395128be3a0e7b02633e4ded0f8922e56afeee65b3c1ff43fb  openroot/bin/0854_SerialInterface.py
f3f78e1281e13f96089a6b2dbac6e6d927e48b2049461c82e4be4a6e591e8d45  openroot/bin/0873_umsgpack.py
1bc66ab979384a89f37605634b494825569e41eba11d3ad1c7ea5d9e9a5f2477  openroot/bin/0885_commitsigs.py
374d4b6a970fcb29e5357bb83a8ba6256c7e4945483a27b8117c3b8de526facb  openroot/bin/0888_pages.py
1df48b1d58d69bc99bb3a24a0360288de1a6c7d6574e166b5364350db8502980  openroot/bin/0889_server.py
8fad6c261c70ef3232cedb2476073cff3ea63a5118a4292fe67d7a4de0634c6e  openroot/bin/0910_aes128.py
2166cd404ec47b7983a9ebd4b306e7f80af64442fce741bdb7f8857dbeb1cd09  openroot/bin/0914_ed25519_oop.py
db545949332f2d1922df07fb0d6a3210208ade407f5b603f2d533f46297d7819  openroot/bin/0917_emergency_rescue.py
e269075461009f6d5c937427d3d63c1fb99ba214828c1bffadc7142cbc12afdb  openroot/bin/0921_script.py
acc728a3df06f99bf6613548f806aaa90afedb47994d3a317389605d733c24d6  openroot/bin/0927_dict_conv.py
f18fcdce4caee7f2e80e4c01ab0457d3a080a872a29489542c6d23c4b0bba572  openroot/bin/0954___init__.py
f55abd83e8f9c689af5ae62623f25377a8ad88f01f0fd15774cf260fd9f8b306  openroot/bin/0958_test_whisper_processor.py
28acb15118ada5c91c5b369c1e970a882ab80f3fe3a2689cb4132222a5504b07  openroot/bin/0959_whisper_processor.py
2d69248d7c89685940cba2eddfdc3bdd44ad925153e68bdcbe8d13918ed162e9  openroot/bin/0975__util.py
ebcaa12df71eecc797cac89de1f3a99a17d6920768ed9efef410b457251c8881  openroot/bin/0988_to_process.py
59fc854aac28108157061ed3ef73f270a9682350e25f8e465a2d3e24eb024786  openroot/bin/1008_annotated_handlers.py
b189a666b2ff1afa1848b701b8f4510df49f81059e864cf0fd9bcd9300d8d8c1  openroot/bin/1025_mypy.py
dd0c90a3a94ddf970eece5c36c511759c35a3e518245aade815640f86fa56702  openroot/bin/1038_warnings.py
e3ffc6bb2bf580bc6e6428708a6f247d036220e709f5a72b785392babbd97e6b  openroot/bin/1049__models.py
d6e5791cdff0ada42fd38e1e2844c5fc52e615dfbe894151b6dbf320c34c01f5  openroot/bin/1066__response.py
19104600819c8e2f4355a49e970b8271058b82c746d5879922c3d1d63b66a488  openroot/bin/1067__streaming.py
1c19d9924067cf1b703997b4db5d82e04ca846fc614d5b53acb143cf6ff15428  openroot/bin/1080__sync.py
23b818fead4168779b6afc523201c4bdba2b00ccba4521580be29bedde8d6660  openroot/bin/1087_files.py
20864b49cc956d47087d82189e0c5834f500e219f1e591071fe8498b64c0ed6a  openroot/bin/1089___init__.py
579bc534e56af94a1ac1779493a8ecb58bb6b6a613b2286b9ce30eac9b9544f4  openroot/bin/1095_completion_usage.py
726ae33618c75e72547e0a776a5d01dace0ef8fbc50fe9c79e2ee1f21da9e853  openroot/bin/1104_model.py
9ed2947eaf679ca07a7ac1662c195ad61614dbd2a3985125aff8b5e087162140  openroot/bin/1105_model_deleted.py
7d428ae88eda9be4b1e1c9c2ee70b798712138a6576e44d11cbcf1880a4ade90  openroot/bin/1106_model_list_response.py
c1a512b7ddba5a00ae4cec9d7bfe175e49f7e8777a1a188f66bd8a598319572d  openroot/bin/1113___init__.py
5495e3bfe97eda94c40995cfddb7cb19364f415203814ddce14966d11269d600  openroot/bin/1114_chat_completion.py
17b015578a0271d2f40634b41fefcf5e53573a7d98c80685e0b7697f50f16039  openroot/bin/1118_chat_completion_content_part_param.py
cfe4aba04f5d582bf43fa93a394baf7f3c3a61b36fdbdba1f5315da061ecdfda  openroot/bin/1132_chat_completion_tool_param.py
575f42aec71922cf1b2f01406c6d6cc3cf67f7a49fd6e16e16195ff02f7ae93f  openroot/bin/1134_completion_create_params.py
ed2e872b63e9f938e12f4f87716ce31ddfcaf82dcf8d8cd633a324588b6bfb71  openroot/bin/1137_function_definition.py
25ac379a69940772b2eef2f57f3b21fbc9002446de631710d093b2ee9efae57a  openroot/bin/1139___init__.py
660a9c9b559a24b0704d0402e6618a368c23953817de67d7fc9e5edaf776e253  openroot/bin/1159__dataclasses.py
b5f75f76940a6384765c23b0a876d97a840cbabe95362811adf86e757047c77f  openroot/bin/1161__decorators_v1.py
fdb79d7355dbbaeca044688b66a914930c05a506a847584a2e5479d359f2c926  openroot/bin/1170__internal_dataclass.py
f2727eb8ce98e33eb1a5ab271a89c432e6ed3555ff9b179e44316677fa8c54b0  openroot/bin/1176__schema_gather.py
743c6a178ea5ceea82a0a2eb007fe4f791036dac8478a6f69478ee4c9e4e0686  openroot/bin/1180__typing_extra.py
413eeb298743b0289327d1848e6b107561d2730a4aaeb3641aaeafa8e34fe914  openroot/bin/1191___init__.py
8507a382d174d3052e40c9e2f78dbd7af83e797c88c292af8ec0fca1fa9f8fec  openroot/bin/1193_missing_sentinel.py
6ba3f459eafdc7871bc0a5bb5eff29a1252a33858ff912d6c17e9832962af400  openroot/bin/1203_config.py
56a5890ab894362132a6d5eba03549e74d49a550347a7d9500d724b2a5cbd9bf  openroot/bin/1210_fields.py
a2fc2d2e911909b9e08596877d2349ba9cdeb731cd90b5e39ffeba9204e7215e  openroot/bin/1220_typing.py
2410c8817b7995ad4b089d6c2d078a863285a4b9e936bf12beceb3da78b77e08  openroot/bin/1238___init__.py
205a1b0f531de491652462969e1d7f4377a98a452bc88f2aa34f6ff0c8892040  openroot/bin/1241_http11.py
fda97fe9cacab8466edb0cafbb8f7745922625d0499e3e6818a3632ce24bd99a  openroot/bin/1243_http_proxy.py
bd1d198315673a8e001e11dc1d51b4c28acc73edd9369019e95c61d26d19642d  openroot/bin/1247__trio.py
bbb30fa865f0a53c6a23b85c95274d037d33d861f5370db9f2ec0abf2fd17c18  openroot/bin/1261__testing.py
72e9803c94e4b4e42dc3adc8a86d250e9c99aaefe5d44125bd01cc8b02602f4f  openroot/bin/1268__subprocesses.py
174cf0cef149280857fcb4591a82b3cea0c2da830cf9ffb2c9306b11810639a5  openroot/bin/1273_memory.py
05c540189c35551bed22a9effa8d116f4a701fba7cbf096f976d711eae76d9a8  openroot/bin/1275_text.py
6167ff8b6663b89a842d17cd97a9d7d2766ea22d3d197a8c64f255b0c24c0904  openroot/bin/1281___init__.py
d5ba84c2393a206dd8fb3ac36a32a2f283d262fab736baa93d441e0d1a385208  openroot/bin/1284__psaix.py
41823ac874ef44c619955c41d3af3154010c10018645253d13bfac243df5eb9a  openroot/bin/1286__pslinux.py
77f28c4b39a32fabc0610c757d0379edbdf16b3246753b78ac8cac383075af68  openroot/bin/1287__psosx.py
28731015362646dfcbadea97febcc65ea354997da449cf3b38329536cce05682  openroot/bin/1292_cpu_distribution.py
e7b0f183d54c8a7520b52086d98aaf1d92c35a618dcab95058fc9ba639ea527d  openroot/bin/1296_ifconfig.py
82092e2000e850e606bb2cbf6561aaa39711ac51727d29771ec9886b0f5b33cc  openroot/bin/1312_winservices.py
ae21cf275c797c51902360033928dd104411ec5c6a56f712a769a3b208e54203  openroot/bin/1316_clinter.py
9333a110136deccfa0e242126f56641b0d9fca7bc780fa42780e1f5006927691  openroot/bin/1324_print_api_speed.py
573698573aa346c676eb21db2917d786527b7d454cd61625aaf7b48e0e82ce01  openroot/bin/1326_print_downloads.py
dad4ae35e934de9bddda1c95ac4a4d96cb054f3e16679418a80aa164cdabd974  openroot/bin/batch_nomic_embed.py
4a63b41af182000607f3fab51c635e62bfd5902d2f34291edd015f5e54cd68d4  openroot/bin/cycle_manager.py
5619baf925f36d0e850a268c11e357cd484a0b9cc0cdb99d7ad6a5a8591e8289  openroot/bin/final_cleanup.sh
3c22e1801350332b1067f902bcf00b4ee508a61aba9d515c6d48ef7abde4a0d9  openroot/bin/openroot_public_readiness.py
8317d9601a2e094bfa761d642948de74804f342666ccc7175eb72d5f2d51797c  openroot/bin/aerocement_compile_review.py
81cb6cb90627c1a52ee0af4d4556a581f07a9247585b4ec525330571f10979f0  openroot/bin/0802_Buffer.py
18ed00749e8cf56a7508c42b70f10b5ee9a39bd2a3f7e3ea88ccfc8d90ba8981  openroot/bin/0810_Ratchets.py
01dd5b79c0544cd645c0c4005c74ca6ff7ea431df2d358ec612e7062dd994520  openroot/bin/0820_Reticulum.py
f9216914c8bff309582f209bf0f0d85e2a78829d714a9b7d6e633f899b7db798  openroot/bin/0826_channel.py
61d75e5ea14ca5866b31de310b0c3ae8923a9c3c28ad166bf3c1bb28fd72fa10  openroot/bin/0827_hashes.py
f58895cc6949c0cba2ee0e3a565f897851d127644ca956be7d42cab82146bff5  openroot/bin/0830_conf.py
ee9e1039b526819d6fef9ad3ec2530acba3883838647376f548381cac8f2184e  openroot/bin/0841_Token.py
06221e498fdf07aaaff205b3964931b793dc2e499f40bbd6e90eb5efb4786ffb  openroot/bin/0848_Interface.py
4b35df485448909f5a2fcfa51bda0a4f4cfdb3711eb4b60b4bfb48b911fcbef1  openroot/bin/0852_RNodeInterface.py
66c7a710e5ce55fb75cbdb4434d69b52660d122cb436967186335680b0b9cc8f  openroot/bin/0853_RNodeMultiInterface.py
94929f71001e219ebf11414a19bfa352fb00211389ef7b266f8ee6a8d02d3f4e  openroot/bin/0864_rnpath.py
30e2b9b2f5228f30d197ff88e5f88cfad5cab326f2bf87e9c506f6da3651f5e8  openroot/bin/0877_aiosam.py
e9bc961b83f4eb73759fa2edf9008c552f638811cb8ccbf0c0fa86c1057669e7  openroot/bin/0897_listener.py
a0dc4a638b36decba5b9648c0bee1a1d5924bf312b609dd8ffae288b1ed9c49f  openroot/bin/0915_eddsa.py
eba678b7a6ceaba7b6e9efff11786e1fcc4138a5f49d8887403066b23a1058c3  openroot/bin/0923_pyo3_version.py
d3cfb3a528837b31e34a5639b4a0712c7d6c0f171f7f78188a094e1ea9fc32a8  openroot/bin/0929_gperf_unfold_key_conv.py
a4a91aba0fd81d5ef39b90c87da21595c361397e065846a850ef0e4f7c7f7fe5  openroot/bin/0953_eval.py
7692714e0cd1c6904595f73c1db791e88c1c800191fbe293ad20d5a46a26e497  openroot/bin/0960_eleven-labs.py
4040ca1a1ecbee00d1385c12a93084d1c5bd46f0b774f07e5ae7e91c4f55e696  openroot/bin/0963_typing_extensions.py
8957ace71c2c1de4734037b105a021cb1fed68db76b9c7c0ec2580a38403b7a4  openroot/bin/0966__version.py
c6bb29b1db0d81617145f41c4d7c51f11add8d15d74cad08a39710616a49d56b  openroot/bin/0973__receivebuffer.py
1954ac6cf48f0dc3ae17aa6d7c88979d52686849b7ca05db327aa5aff1a26a1c  openroot/bin/0976__version.py
743e4077827a8407c5e9407304ee2ca92b35876c9b4154e1910a1f2d659504fd  openroot/bin/0992_introspection.py
d4f337d727ff906a66fc7ec62e734546420f01018f2fdce1eab7f64b1a215718  openroot/bin/0995_core_schema.py
20ed8271771da68bd170b4dd185181e91c8165d126da1fd33a6a02738ac42a1a  openroot/bin/0999__models.py
cd28b5de6002a250679278d90649d40ba84a343413e02ea28e77b367eaf44f6b  openroot/bin/1001__synchronization.py
545ef72d1094cf722b6f9c55b75de36f7340717567105e93d7e27438b7de6790  openroot/bin/1005__migration.py
be1087ca84969d7f8427ec166f9aa3e31c91b2c8065a74d07f3429e06499f6e8  openroot/bin/1007_aliases.py
e17f567b48e3d4a2f006dbd84a40055cda27e3aceba4199164035fe0b7f06d78  openroot/bin/1012_dataclasses.py
e881de79612a9543d152fdd5f805e217f5bdd5f836270fccdced25df827f7b20  openroot/bin/1015_env_settings.py
0eb1023c25a1498ad0f016b83bc84acc800cda2f460474d75802f36850e92dfe  openroot/bin/1017_errors.py
a74757f08d0d1077b1b37506a784ac66eb62321b17aeb5a5ebe1a7a956f488a3  openroot/bin/1046__decoders.py
fd355ea802afc4990a1ddcfb74579be2cd0b66a41781e1645d281f88704aff5a  openroot/bin/1055__utils.py
64b819503934e2c6744a82fa0261323d1207289f7180be8fa44cac6f4add718e  openroot/bin/1058__client.py
ffd82e41fcd89cbdc336db9d5f95bb4f671d4ac931f3d0790057e13d00f13149  openroot/bin/1059__compat.py
3630b39a77ea62bb008a450742283a37d41fb9355b2a2a6e3f7babf6670d17e1  openroot/bin/1081__transform.py
c1de8d7d6be3d32a2abd70858918cc1a9665dd544e2dee375d5ae9b4e7886842  openroot/bin/1091_batch_create_params.py
51da0108d5c6f8413f53dd548adef7b4266de14a019dcacbf054531db656553c  openroot/bin/1098_embedding_create_params.py
576c1fe599439f308a35174729b72c7d7121c01de3d152077342acf963132c2a  openroot/bin/1109_transcription.py
0c02cbc75e39fa13d62723c81592aa19b82fe85f7ca39bc165396ffe5c3ffd4c  openroot/bin/1112_translation_create_params.py
f945d5fa5b01c287a99d9968e754bb156521236c8e17397d1b981693d4db9f8a  openroot/bin/1116_chat_completion_chunk.py
c0335ba8d961819f3a47741def31a15633978be299c80b11c61d246d2422d12b  openroot/bin/1124_chat_completion_message_tool_call.py
637976c0e5c8f28862c313a125f841298b5d7df20016168c07d603e1b6454b6a  openroot/bin/1140_function_definition.py
868e0db77e4894709afb11dbe9e135edbdc8f6bd11ab5eb991be27af87ae203e  openroot/bin/1144_speech.py
2303e1dc33df6b65eadeb06e07d371f25b91d80d62ebd41d7937d659722e0958  openroot/bin/1168__git.py
2682a663826b0c1bb79c6fed088ac982d249135baaeafdbd4ef4f3e449471398  openroot/bin/1173__model_construction.py
8d07e726ec83c50a5244d846dbd208f4f5fc7b836fdaa599ac4c3696a8a1dd41  openroot/bin/1175__repr.py
17fadb41bae4a289a0c6cb24747a4fd23509ed309f7b40400c0124aba089e273  openroot/bin/1177__schema_generation_shared.py
ec64e35d758530b89be1dc50f8779a8879406624760761bc6f2098306ae6438f  openroot/bin/1183__validators.py
1a177ebe431de446020a0c821ad3ca3b9f27a7d704281402eaa9017881052368  openroot/bin/1186_copy_internals.py
8408e04a58e82211b1dc0569229baac3948fb6d04d35e181493aea48c9cd8899  openroot/bin/1196__loader.py
988c0f103e6f18ce50e6fe02e19d493e5753447fa89af132947ea4b0c84e98fc  openroot/bin/1209_errors.py
633c8a4d937ac79435446277590f6337ebb01c9c4bdd6e2aa19ab07195eac568  openroot/bin/1211_generics.py
116765dafe2d867007cc9a6a8d4e21d9af03522180bcd896ae48a2f697e14dfd  openroot/bin/1224___init__.py
7abf53e37eae49eecd2eb7e22dae31e8dbaa8398af43af770b1598096b206c7e  openroot/bin/1235_mock.py
f5ec4639bdcf07e329d93d7eb1c91278bdadfad27ff7e357a2657c8a19960a05  openroot/bin/1239_connection.py
6be4fc2d3b14c5ceebd16c356ad7c7483a163e34347c0f1497b4b7f85d0c8fbd  openroot/bin/1240_connection_pool.py
6089c109a6e211e4be51a3ff25dc5ad426850bbd444cf5bc1d94c720cf11b1cf  openroot/bin/1249__contextmanagers.py
1d8be76b58996d67302d13933ba2212d7efd45344b3d28593167b4b06d6ae782  openroot/bin/1267__streams.py
4fc5eac1ff0ae8481444fc5bb753788bb03c04093e81272ff864618cb5c87ffa  openroot/bin/1274_stapled.py
30c2596498d0ad48bde5100d34cf9aff9e4166ab80fe0bf8ac7535a5ebdc4c23  openroot/bin/1277_test_sniffio.py
552487df25432a3f0dba4217f4f62dbf096978e9d9cffc23b6e5dff0c3dcff94  openroot/bin/1279_setup.py
671e9e2d8fb435150514828fed2c9c92d803a28b6d767940f5a5fccb87bbe1d6  openroot/bin/1289__pssunos.py
461cbfb84a8d5b9a6d3601e975af98b4fae010b5a6b50ddf354cba209ab1a205  openroot/bin/1298_killall.py
b2c888b2bf3afadbe3de13ec8a5d02c8584e4594f0f2d6bc7ed6274e392e57d9  openroot/bin/1304_procinfo.py
d542fe3c5fbadf06d3570047e72cf9f555fbcc81492b4fb964397d202050c7dc  openroot/bin/1314_bench_oneshot_2.py
cfb1cdfa0a041a007f3436841a1077f7d363136bd9d6c164f4eb429303780427  openroot/bin/1323_print_announce.py
4a6f2a97afce0182e2e2f875a5aa0b6fc83b64cd4990bd2a8ea8404491ea928a  openroot/bin/1330_winmake.py
81ceb6d55be08f635ac6eb01ff31b07eac0ffe7a77a9a090a899723eba750f49  openroot/bin/1331___init__.py
94acadcf1340ef665d861cfa8e75e35519bedfeefd8f5cde9623ced5231255a1  openroot/bin/1347_test_unicode.py
6b0acae267077a62dd0d2b87249db1cc972f483995e8a5bc36f30ec7ba95e7f4  openroot/bin/thermal_frontier_v1.py
b3909109c25d549d3c8871803515544c64bb781b89638a0a56c063fad8c8fcb5  openroot/bin/0726_purge_installation.py
03b7308e0a4dfd52fceb70852e5d153f16ebc696f0470754e04c16022f1913ed  openroot/bin/0735_nrf52_lto.py
92a39299b27e3e99605c67c31b5cb794a340ae70da9bc112a23a43d66657978b  openroot/bin/0755_emergency_rescue.py
a751036332d6a4592871c87285d06431a1a9fafbde6c1d5bf7245dc5051b1ede  openroot/bin/0763_logger.py
7284348dc3c6facccd9f8b2d9bfd2799dac89085538fc13ed21c44dcbfff528b  openroot/bin/0764_psychrometric_model.py
be9aa3dc2d1ef36de38c9d6648a99e2e393bd5cde8f3a35d5739617c76edb73d  openroot/bin/0771_import_euclid.py
67066a546000a59b9dddb0f3340d5104406eef77835df731787bc51970f35dd7  openroot/bin/0782_theorem_generator_batch5.py
84b79b011ac247adc09d21375420f9d12a2e2ca63e676d656f543d9b5520a3c6  openroot/bin/0783_theorems_extend.py
53585d565fd5252ac1019f79415af05eb46372788f6c01d21d472e35be052f96  openroot/bin/0784_or_coder.py
a2b707c7985b55827af0686d8fe3475b66f7afe1e9e1cde7783f1f96882076f2  openroot/bin/0788___init__.py
e5d29a9f07645057ff4731b644d6e408b487068725584cb7b6ed9e4b5a393627  openroot/bin/0792_rmh_lab.py
6f173009ff373d7be2904dc1bdc69a1d383421a00f4e3c64887e895ef24a6abd  openroot/bin/0808_Link.py
24483b3e63769d02770f6df8f4888e510519df3ad4208e9dae0053841b89bdea  openroot/bin/0821_Transport.py
4eb8a5ec3e57be97c72d64c088347d9c5d5b6f9eb4f4d197b775f1fcdc0b481e  openroot/bin/0825_all.py
415cdc751bb7e9d4e0808f8e6cffd504bce18ec14d1342e342b0cd0d21e0b462  openroot/bin/0832_Ed25519.py
6f785d4396416a8a037f0ef3a9c0899d134202208859d36ee8eb1d7f8f4a14a1  openroot/bin/0840_SHA512.py
ed13482cdb51059ab8d11e6a6a9387eb93eaedeb62eded2ca873f6152689d153  openroot/bin/0851_PipeInterface.py
723887b15dd321920b6130c2c063174fb22ce85485b6726c38dfcdbfd3e146d2  openroot/bin/0860_rncp.py
81a64c7ca27c279a6f242bcfc60cdbbcd01136367dcc29356b370d6f1cb4f321  openroot/bin/0881_tunnel.py
f5e2e54a7451f7739271e819202cb1296142accb81c5a8d6d66d080f44c54aca  openroot/bin/0884_client.py
6a1da02ee62cc39ab31b357468ca515b310f213186f0a033fdec9ad886ba9c1c  openroot/bin/0891___init__.py
e660ed7d4dadd380139a0f764b907eb1c51c7630b2d5906aeb6d32dc69a976d4  openroot/bin/0892__version.py
95bb35883e97e205ea0bf5a2fe98769097bea60896384c5c61bd03e1a93c52f0  openroot/bin/0893_args.py
b13a8e6c23a5e887db81cd8203fd155d16d29883f325c35afceeba6014ebddb4  openroot/bin/0900_protocol.py
0c09dd34458462622ed8f8714efdbb79d918d365ad0c4b184349c25f97d48735  openroot/bin/0909___init__.py
fde5cc1570899cb2799ac66a85a14547a90153836b5d697750df955adc88fe84  openroot/bin/0916_emergency_rescue.py
8e859f85007d1863b0d4a6907cf348cbca74bc7fee8a11a4e0d6d34825178ab8  openroot/bin/0918_compost.py
b172e1ee0dca0b84021717191814e91b6b1c47b866981b0c8eae8ba91a6d9118  openroot/bin/0925___init__.py
cbf1753148dfd388c2f78392624430a7ef0a0be44bc1205f9a7fb5970474bc23  openroot/bin/0930_make_unicode_egcb_data.py
9cc282dfcd9a24da03ffa1b4123b5508ee935e19e369c33520b1a73f89440094  openroot/bin/0942_convert-h5-to-ggml.py
d91418a3ee9c2bd11d6f3b7ef8db97f290c0b8b1fe93f83bfcb060236492d374  openroot/bin/0950_bench.py
f746535bec9f74f17c796f5498cf6c98b4cbf10193b922cdc4e6c80d19c26211  openroot/bin/0957_generate_cu_files.py
cee5cfb7bbccaf8ee1676ae772c0881a65684be25114e84de08341851ce2a1a6  openroot/bin/0962___init__.py
6b8472a4e454082dddd2afe4c4fb8120cee34c3f222ede57f754c7d05b1db8de  openroot/bin/0972__readers.py
a052a6e8fb637877db8f844b5fb541eca0dcd60218e778171b7fc747d96d9930  openroot/bin/0977__writers.py
6eef5ddd389fa0a72264572a441bb2815dc64ae4e19d50ff9b620ae1ccfde95b  openroot/bin/0979___main__.py
258b1b68268807f222b7a90d86d5d2b5e246b783dc43b9dcab49c8a5c7a522b8  openroot/bin/0982_from_thread.py
b2baa648d53888e52f585f92ac9bdbf06fd811b1c510b39740ec1d0c80534bd7  openroot/bin/1000__ssl.py
fd12e05d8380602df9d229002d5e7d199ebc209adda1c459c4fb3d3e39b37456  openroot/bin/1003__utils.py
617fa3500a6ee4029a55628fa1a57e9fee25ed46d2ebd184b7d45ade1b3398a2  openroot/bin/1014_decorator.py
35b842cfe92ef300e060b40c062ef93afee1cb075cf0b7b0037a1434867c2554  openroot/bin/1024_main.py
80207dea0b741bbb625438559c97e92abd4044be6a907f923d992e364986d8ee  openroot/bin/1026_networks.py
70e328796769e77e8a17ce6e448716fa8cf53bb7791910a9c7d1d34b8fb5b9ff  openroot/bin/1028_root_model.py
a706c825755bd42576980138c3f1067cd8fb0f0cec29a5b0fed4cbe9cbe24eeb  openroot/bin/1036_validators.py
0ac6997bac998f4ac783adf6d8058a587193315afdb718047c3e4fdff46bcfad  openroot/bin/1039___init__.py
2c61b3ac94d1dcebcde0c6f519554d2d7917247fbaa0a97002db4ef69e70ff28  openroot/bin/1045__content.py
bf05bc20832732a09b2bcbc02e127ec72a64691379b78e1359d94e3cfbecef6a  openroot/bin/1061__exceptions.py
66843fed6a06fca41439f87388b53ee93eb08e3f99ae8380b4db26c470fb92a9  openroot/bin/1069__version.py
9d0abe8856b96314da5b249a2e281ab5ec39ac781347433be453589b89ab3b5b  openroot/bin/1070___init__.py
a111b2b451d944bd245b5ac43859e177f30e1d10cd710ee5f21ddc8130e269af  openroot/bin/1071__compat.py
6e5f79bae216c2049f5d7fa03f5b6b2bf94300fc09ba361f274e42c68d92102e  openroot/bin/1073__json.py
0e4dbde257afb895cfe5ee26db46110c36453e5ef37a05ef73d29bddd502c092  openroot/bin/1075__path.py
6a09678f6c814c3c865fd02493672b647ae5d74a2a46671e532d99a74d3c5c4b  openroot/bin/1076__proxy.py
5ec362fc05b3faa1416f943635d998a4b2011f7893ca95c30705c034f6ffc9ca  openroot/bin/1078__resources_proxy.py
4bf1c33e992bff6bacd768f533c36c5d3ad383a4494f6ae0237cc0b19a4c4998  openroot/bin/1096_create_embedding_response.py
5d0f03055477593e1b3f9c48fa5708c446d0092f8feff56813d1bf61daa16237  openroot/bin/1108_speech_create_params.py
9529211efb97bf69b8a453671ef2b9e587ac0e94d647dc2769c505a6d9a28ad5  openroot/bin/1115_chat_completion_assistant_message_param.py
fcb8a2d6e15c49b5ced1b966267dd51e4617b9728ed9c453f99f898a40f69ab0  openroot/bin/1120_chat_completion_function_call_option_param.py
8c86996c11c76ede2fe311c2232bd8b582ecb7f5f88cece746360d7137f4305d  openroot/bin/1121_chat_completion_function_message_param.py
ebe8a95057ec5cc7f92fb143162d76ecd695903b66128a15806045e93b3deb90  openroot/bin/1129_chat_completion_token_logprob.py
04f952556f636fb7d3cceaba9c5680ba97d9ed85d55532a7d49e5eb5a497e229  openroot/bin/1146_translations.py
f10f4e0d1a35c08a456b7e1568dc2e696166c6a1716a00ed52120091036fc445  openroot/bin/1147___init__.py
3cf5f351457c654b9d475fedb632e3d9250096aa4944b04d7ba2d0feb2526a14  openroot/bin/1148_chat.py
865dfe4d102bf365368d3c8f3f7b7e42ab2f28b8abc6d90b7cd7eb37e7e9d31f  openroot/bin/1174__namespace_utils.py
8bf6fac2d96e895599461d5963c52f076519ce23f52a3a925d9802f87c70393d  openroot/bin/1179__signature.py
4c19ba6c9ef026c36287ff16ab92330dcc0fdf69bdfef7f1b3de9d7ac2ee934d  openroot/bin/1187_decorator.py
e4ce487356d99e384d0f1b510d529b44f4d0ea9a3a42e28c63b320b8c907796d  openroot/bin/1197__schema_validator.py
e10cb5910a6adeb3556497881de48f0e9b92d81be1a7528fb73246d71bbe1f4d  openroot/bin/1205_datetime_parse.py
07397e45c9e2b4f0479eac308fd8afec98c7b8dd46a67587db874a905de5f5ef  openroot/bin/1219_types.py
d4fa8e225cfa3955b019db371c12a5c3812de9ab05a2ed1452902da3b8c5382b  openroot/bin/1221_utils.py
9725249f5316847c65097e597c48058ff0801e88e888f71a41e31d10cf57be25  openroot/bin/1222_validators.py
e8e70f5ea3047dcd01537f3ffa21d4343775bca4937365154f4f57a8d6ff04e9  openroot/bin/1225_connection.py
15ccc5c08803a6790ad1b3835895cca6c50961dbc00f4e24694686cc953c0cad  openroot/bin/1256__streams.py
b649a43ca12411a88c0fc0bd59164196682339844345b65db5ee9efae9dacb61  openroot/bin/1257__subprocesses.py
0d05645d4bec4c460a9013bc765554ee3ff91fc40eb4bcb8b068b55ab8ea7afa  openroot/bin/1276_tls.py
a68570bb242bb25dd504bf2ab55543630cef69f0acaafccaebee1a2e7c358cce  openroot/bin/1300_netstat.py
f04412e119806c016e1cb271b925d3caada0d8534eefd87f9dd1a24f5d609b47  openroot/bin/1302_pidof.py
bc12271246e57343a1e9d209467177e8f413386cd2c355550b556977c9980aef  openroot/bin/1318_download_wheels_appveyor.py
f3413f2b313e2e0510789358c2c5eecd5e5aa4390f96caa4b65396f5f80a86e7  openroot/bin/1320_generate_manifest.py
f122a3170edc4776f2052865bd60334123938e38b90699e4f09c9492c4740102  openroot/bin/1334_test_aix.py
a73c043146b3e9787c02637faa20a6613536cb3a2dfddc2c75b4df15d2bcf559  openroot/bin/1339_test_memleaks.py
b036a6f6f749256b9835d768be1c62d5cdcafb3e007d3003d1f432c9a783f186  openroot/bin/1342_test_posix.py
36166c1c00492a30840f3180ed92fadace8d96aa49c29a03c9b68f076066f471  openroot/bin/1344_test_sunos.py
32259f16aec31325ebf0676fc029046f7a7c36928cf5c238d3c07be7658fdcd4  openroot/bin/1350_dag_orchestrator.py
6aa29ef9a47f5882d7bd5b17309cdcf141b818af3587a14febeac8b281aac9bf  openroot/bin/autoupdate_loop.py
c41aea80e79e9f05e731276d5b823ce94773301408d918bbe3cfea92bb355f11  openroot/bin/local_rag_search.py
d861a6e239072359712f5e9cf7a345240a49d1ac2c6c7491daa2ee579a01ae9e  openroot/bin/0795_openroot_workflow_manager.py
35b02a53e1b2b3e7f6aa59b0b6ed354ebc2b9349de791e001b43894542d1d70f  openroot/bin/0807_Identify.py
24159821cb15f96bc41f0357056e7a9dd2f9990ab1f6dd00602ee331a87aae9b  openroot/bin/0812_Resource.py
4bbc2df3f1e54ed821c4de00b60cdf5695273d8b963cd63035a0e816052f4151  openroot/bin/0816_Discovery.py
3c555332fdd24b248ed4d128d1051142b708286b0ff1d82e18cbf7bfe3f27828  openroot/bin/0819_Resource.py
5737c3cff95a960e3b23cbf11f08626d11241bff1c6a21993fb0ab8efc4c1a50  openroot/bin/0834_HMAC.py
2224cfb2c2fcf8878c1ada746ae863076e8bef4ae9e3a8fa7af59efc7c61da78  openroot/bin/0835_Hashes.py
790544298f8784cf6e13ea55c44a01c12f658f15899ffade6ab3ccf0092482c4  openroot/bin/0838_Proxies.py
b3c6b13ee9a90b9c1f1b59e74d2bfbd1dad47fce313476772eabf4394eca52d7  openroot/bin/0842_X25519.py
08b473caaf0b9d1542d028e8b3046b4efa55a8566fcd2ea1afff02b23f9d676a  openroot/bin/0844_AX25KISSInterface.py
8eeb6a8ca085988d70cb6033ef8ccc83927de0c6569c1d6edd5f3ed8e715841f  openroot/bin/0845_AutoInterface.py
4e569d4ffbab05ac6e58b551a8ed000a6e3de903175748caf7ee7c816ed29625  openroot/bin/0846_BackboneInterface.py
5eeb0cb2caa2c3a52a28c6848d98e7f53d74928f9cae1585a5efcd9a510c2a24  openroot/bin/0847_I2PInterface.py
43be8ba69a68568e8e9cd471479264af27e1922ee6fce77b050c34e37e4477a5  openroot/bin/0865_rnpkg.py
91ad2fe50958c5219cef04af63075faf3400c3a6cac162724bb84b41ab55d9a3  openroot/bin/0868_rnstatus.py
d77bd746bdbc2157af3511aa59051d8e2853d9ff883865c5dc0c9afd9c1f0be0  openroot/bin/0870___init__.py
8f91f4270e0811a75d1e80b76349da26f89c12c3c5ef33a365681bd9b3f87e62  openroot/bin/0872_platformutils.py
4ed21736777d852c81a0367f715e02f074f0bd2cc9ffe2bd4197749c7c1feb4b  openroot/bin/0876___version__.py
9713f76c42cef2c0104619fce3862d707c93691f81e2aaf14f0a62238cf63a08  openroot/bin/0887_main.py
643adaebdd16947877e6291bb4e178d1fdf0bf334856541c1bfc7e49e9902518  openroot/bin/0912__ed25519.py
c0a47fbde13a29eec3437237d53f9e1b9a16459a39b181b69641a02b26388d4a  openroot/bin/0932_make_unicode_property_data.py
d6a788dd91e4f8d9083826583d503d8b3eea13f8aa5d9d713e10123cb12e48c4  openroot/bin/0937_sample.py
e874333f95c52725c23541b39e71594e01442a2a687c96e2e882493c45b887a2  openroot/bin/0944_convert-pt-to-ggml.py
7e4cf0ee6988f835bb0255a5b0e9509b4b4e04cbc8c13e8da69b034bc28d1aa2  openroot/bin/0945_convert-silero-vad-to-ggml.py
35d1d54f84f43e9ee7cf80ac5fe04cf9c4913f2ce75d2436faccb1e843b4f279  openroot/bin/0946_convert-whisper-to-coreml.py
3f74f13cb2ccc585d42c07cb4869234013a02bbb2c408378171fb698ad3c928c  openroot/bin/0947_convert-whisper-to-openvino.py
8a64a41a471818441b1cc1cb43d4f854d5cac0df34752f2350cca44527cf78af  openroot/bin/0948_generate-parakeet-test-model.py
2898e4672aeefc9f44cb4de38c115cdf286f5b35ae321433467a7674ce8841d0  openroot/bin/0956_english.py
23deda5e86a5d56bbb7642f9e3c04034150290e21b7bec790a2a1803d201635e  openroot/bin/0970__events.py
ff92c6fc1191f0509c1507813c7f93307826ffe07e1147160a74287fff578c51  openroot/bin/0974__state.py
d9f1e317e49f80fbe3c8d67588787fc23a96751fd8a393831f0642d232c13e17  openroot/bin/0978___init__.py
5ea6de7da7008434f8cebfedae76c0d79798f2f74ae064e08609af506ac433fe  openroot/bin/0980_distro.py
cc7157e84a5c31b189f05cc16036cee7a6cfc31fc360855229b64cfb8077fe58  openroot/bin/0991_test_cases.py
91a8d5821f09ed467bc1389d571cc53298f04a71460680e84ea7d5000bce1d9f  openroot/bin/0993_typing_objects.py
e62127278c07bf5384cdd2903f368a69929f3b8a524000bae4e0eb608ebf4bc6  openroot/bin/1004___init__.py
033a867d540717ddbf65cb4372e7b40cce324e9d8fead7a49304483535ab2c8a  openroot/bin/1010_color.py
44aea6a804dcf72303f8a043f48252f47a4a0a9ad61ddf30a3ce019e6fb77d1f  openroot/bin/1016_error_wrappers.py
647f11908ee1e01cfece9f0e7530316c952856f72853e8e131d459d01fa4d317  openroot/bin/1022_json.py
62bdd0c1a5122b5eeb198c7eee3f85762705233cf863d14557ed45e3eed15d7e  openroot/bin/1042__auth.py
272878d4642aec039ebfc20e58a0c083bcc26ef1c07ee7e65b983f3e24ed12b6  openroot/bin/1052__types.py
757f7d551d4348e1e9828f40abb3f360ee0529dc6a2a3c32369f20adff1d1cdd  openroot/bin/1054__urls.py
84117f49bdecc07c46f676076fed0485acb29ba02e7f6455fc197fcad0005e63  openroot/bin/1056___init__.py
4b5e0f173c8df7e237d70895ed298894be466b430b1f176f7a022719d5c7eed3  openroot/bin/1060__constants.py
35397404ff83bda928a1ec027babaa44190eec95a4278a5c021ff63190cc1a20  openroot/bin/1062__files.py
c232088e7ac4b8b293d9030aabb132a8bdcc023f2c0735695d9dda88d80ef81f  openroot/bin/1065__resource.py
6c0053b3405ceab69b745be72305e312158bd794dc460599ffa5c64ea37cc549  openroot/bin/1072__datetime_parse.py
48c0bdd1d88515e729120ff38034556dd4778521088155628f8b5a0fe9e830b3  openroot/bin/1079__streams.py
40c607ea019f43ac6684ef878a7c486b895c4121e8a05f11ea93c8a76482d8d4  openroot/bin/1088_models.py
7bda7904dbe7b454480a05d61d5f39387718e0564fc4098fa86771e10173dbc8  openroot/bin/1092_batch_create_response.py
5a8a9006b173e2a6e2e50198075784207ad640d00e1cda1641203b4cf7a924e4  openroot/bin/1094_batch_retrieve_response.py
d6feddf726db1b9983f3eb69ecf85cf15175589ae7ceb42b941bf4aeebb4d06e  openroot/bin/1102_file_info_response.py
fc94c031875b4dceb485279d5ec310845c8b8b58c6ca7ada7fe220e455369357  openroot/bin/1117_chat_completion_content_part_image_param.py
4457abe19617c5579df45d2e964aa2d31372fde3a1a7add8fb4a0ddb87615412  openroot/bin/1123_chat_completion_message_param.py
77b7599d7962d93c2d4c2c2994a12f7ab435890dbddc94679c6b19a75ffd87a7  openroot/bin/1131_chat_completion_tool_message_param.py
52fc4acffddbf5be440b05abf1116b207e75d61b5b536259b29f59f4132417ea  openroot/bin/1141_function_parameters.py
35c9419a520740ca735c85ed79f43b7df70f41015a381581fd6f41bba705bedb  openroot/bin/1143_audio.py
19b52805200ea7bcfe97ef63e5884c851dc3308727e8554b863d3bd8edcd9e7a  openroot/bin/1150___init__.py
3d3a34779ebb4484d7c46ae48ba90deffebbc300317f088c0dcb972626428c4a  openroot/bin/1154_mock.py
4d18710f93ae63a094a2c8a805d05c254b34a26ec820e36265d60057bcd0f233  openroot/bin/1169__import_utils.py
3f29d020543ad7fff819caf39f40f910d96583b8cfabf731a0b4e6b8540163cf  openroot/bin/1171__known_annotated_metadata.py
c2645115206fa9f70b6c8e353ec165881e2ed80677989a597a21116c3df1293a  openroot/bin/1172__mock_val_ser.py
80de3c06c47e143ac90e26c29a8ebdb6d420ebb59bb85addcbfd4d40bddcbcb2  openroot/bin/1181__utils.py
1e55821b7e5146bc72cee4d2e8b4d089907046198365699ea901fcacb5bac00f  openroot/bin/1188_json.py
1b377a6ff83ccc95dcb84ed046ae5a761c7f10c25a8577dca57085d1182baaa2  openroot/bin/1189_parse.py
1059e35ffba5a7eb4fc948d05f9a6642dba0d4e14bfc071cf1b70c6cb77e7d56  openroot/bin/1192_arguments_schema.py
6aa06e03ef9cabc8005648a6e4124f140487cce67c745b66157fdf346afa8a9e  openroot/bin/1217_schema.py
ebadb931fc3daa40b63708ad07f2450167bc07e5efeb3054eeb2fd936f2d7f2a  openroot/bin/1208_error_wrappers.py
0ce210dacd9909ff6a7f0c61ccca6b4cf2ea08bf0ec465e2285eaa447c6f5726  openroot/bin/1226_connection_pool.py
8d389a58bf37a60a460bdce2bfdd197f068a34c987c2639a97368a8ae4f1013a  openroot/bin/1230_interfaces.py
c7c3e01215d10bc6d5aac77393f609c7c63a77d4ee6f4e82b944b09db9adaa86  openroot/bin/1232_anyio.py
cced77e8f2999ac6930caf87464f38780f8c520f3fdb025fe0dbe62b8df6022a  openroot/bin/1233_auto.py
3a6543adf7a656f17d7392b5b6906043257a7e7e6fd17c821312c0a81386cfda  openroot/bin/1266__sockets.py
057828012a484ba71cc398d3c7857e1f67ccb08712bff350e84a33b3116063ed  openroot/bin/1290__pswindows.py
53040507ff740a3435ab83e32369414236f7945d01b7721ff9ba7a212115e88f  openroot/bin/1295_free.py
b408ab08025347f2cb7a1cdc64e6cfb6bfd37df36c49cae01cf153d8ef93ccd6  openroot/bin/1311_who.py
ec875ada9fbd6bce76eaa452d3e332f085e29256b9caedcd22e1bf0c80785012  openroot/bin/1315_check_broken_links.py
a31c441c4b82ff59723e97b0b6f5672d25be55ae13b56b94a3c661c603358edb  openroot/bin/1321_git_pre_commit.py
5ad4672d9e604b7f60232b0b0a4795f7d870e4bbe8755c0119eb287a7f4830db  openroot/bin/1333_runner.py
310b1ea4edb94e57f275a3b18ea80404ce16ae2f529c2524a412c48909cabf64  openroot/bin/1341_test_osx.py
94eab79cec9042f2912516934443b4181d04ace40665eab11ec11b9f9aacf0fe  openroot/bin/1343_test_process.py
07477cf6f06cc637e18952525a1456f9c35943e7b44a4305efb84903183118e6  openroot/bin/1349_bottom_tier.py
1d30881ffd1bc3705e1539078d963a20d53ab1df5b26055bd11372ffee44d573  openroot/bin/1351_meta_upgrade_20260805_000212.py
421d337a028e6ef8a95a1627be8edd9b5ccd9fc21feb997427bdffaa59b78e81  openroot/bin/register_pathway.sh
f1ade9f8a2e71567beb64155ecc298dfab6a7f0b08386c79e5997198aea48132  openroot/bin/unify_v2.py
c91c82c26fb74419102b39b69f2fdb2ecd0fb18aae34833170e9b068bbb06a7a  openroot/bin/0794_ecosystem_dashboard.py
c7f5fded801d665cf546688a3310b8d16831e05e3837baabdebd871ae1c5c451  openroot/bin/0797_agape_engine.py
67dc19bd317eeda4fde3587fa50e278a8f9c9d8409749b9459c2ad2f2df2c435  openroot/bin/0801_Broadcast.py
16453a86167bbc88cf1e5a76043292c8953e96b5fefd3adfea96d4bce96f66ab  openroot/bin/0822___init__.py
831128b5e623333d5ed3f99afcd213a96c29ec16e34abc89075747bb231c70b5  openroot/bin/0833_HKDF.py
d962ee5adc701ea9b7881a29a4bfafe3742458401faa6d7bea3e469353b8043d  openroot/bin/0849_KISSInterface.py
eacfb7fde3a4f028f1f7df81dd902ccf8f7b37182f617a0a0a934ba4495dfa74  openroot/bin/0855_TCPInterface.py
2a37ea6da897f940041786fbff39d5a83f4de633111778f77fd79d3e03e7fb92  openroot/bin/0859___init__.py
af67f421cbe5ef6ca8ef96d517ec8127507758cd1b191f89c098d4a2ba88fc57  openroot/bin/0861_rnid.py
792137895542e0e81e117d73116f62a04b2bf4ef72d2ee8367c00a8151707562  openroot/bin/0863_rnodeconf.py
37ecf43f5ecf212349b20ac6f6b9df9422a8cccdf506e1026f8dc4555ee4f558  openroot/bin/0875___init__.py
697c6851b4dc8d17134e8c410bb6d78e88dba90456391aebbd53a0843cb02c67  openroot/bin/0880_sam.py
0b6f1b5f884eaf81befb15a4fcb4b22831ca31f26c7716afab20efd220157b15  openroot/bin/0882_utils.py
affc573545c1088f2b8565feb8d3754f24dbc461730e792c15183938a1a86963  openroot/bin/0895_helpers.py
5a79738b07674df0627b4dd5f96ba77fdc3261df3764ba5b5098cc3474b6e739  openroot/bin/0904_KISSInterface.py
ae62459985157f0422bc4db123efb640b32f39325a71c5d174c064c131a04849  openroot/bin/0911_aes256.py
6f34a845785f53425accf30759edc566873fcb0c2188648e07b09c898f39dddb  openroot/bin/0920_generate-encoding-data.py
1bb9c7b1feb77d10149a929f87baa03f5f2d6e4f4b771a1c4298ef076226225a  openroot/bin/0940_server.py
d66ca2f513164bfa6ce4a28780303ecabc1bdd18982e7c869797d78aba6eba35  openroot/bin/0941_convert-h5-to-coreml.py
c41f8cf33dd6b1f9b9f8ae7ea5b3fe754d0fd0917e3c580d03c56b0da38ebf13  openroot/bin/0952_eval.py
f0818a8edcf2bb18bfdf46daee06961c7149045225b01cac0ca13deda194d3d8  openroot/bin/0961___init__.py
c9b8b1af4c6cba99e403a18503232e6ee5c5e9373595bfe117cf743600ac7cd7  openroot/bin/0968__abnf.py
1e2b5421fcef0288d279a1d5989f6b167f24ff223adc6eacfe350bd900a17f85  openroot/bin/0981___init__.py
fe62e782b332f7b4cc47a55b5b863a6330d493d66e3dc40c3e592ec918770bd9  openroot/bin/0987_to_interpreter.py
402f9680cc4caffc10fe6357512ec055ffb684b121befb0f6353d0ca148639d9  openroot/bin/1013_datetime_parse.py
d19a99f4ef5a9e7223ff7986051aa9b3886d7b2ddbe65575f9ddad5313cc3270  openroot/bin/1021_generics.py
4f4e60f1641ccc1b1553fdf945d2b1823222ed8ecb222a7aee9177348ed7e061  openroot/bin/1031_type_adapter.py
2e853261e3974e2786cee3ffeb850bd30c5db718eebbf41b3af13b34e83e22a5  openroot/bin/1040___version__.py
c43f941baefe58c91e96d00039e1868fe719d91453026d7db1647194563bff8d  openroot/bin/1043__client.py
3d35a5b1f44312785d890eb504f58fe11c0fac8764c890148203668c561af642  openroot/bin/1057__base_client.py
be99ae4c3dfdb57fbbdb449fa659388c79211ac2fed8a13584ff1ebe3649c94f  openroot/bin/1097_embedding.py
38856020ffa5220e48e1e219dea0c9dc431d73950970cc44c9ceced194538795  openroot/bin/1100_file_create_response.py
7cc830a6e736b915f4100cefc116304ff93670411ca0b869ff0be83632bd3149  openroot/bin/1110_transcription_create_params.py
9a293e3119306f9e370b9152279d8bb5391e03613f1dd2d482da0711d3bbdd74  openroot/bin/1133_chat_completion_user_message_param.py
7a88821c629e635fd88ce9f8d4cf10c6f21423f33af0bb6caf577aee0fcfafe2  openroot/bin/1135___init__.py
0e473fa66f7ccc22b2a2e42662b97ddf870af19597ee1798fc8232ba75bcc7b7  openroot/bin/1138_function_parameters.py
443106fc96aee4d88971f3b4c60753ec43a0b14d4b816218957ef0379ad8b55b  openroot/bin/1160__decorators.py
7f2ce74801e1e40ce88675d94ad5741ef1fe9d16dabcd1cfca0fa49f1f92fc41  openroot/bin/1163__docs_extraction.py
e67dd8efedc028b9fcfc54b761cecabad2e23d48725e602d90464e6859e89f03  openroot/bin/1165__forward_ref.py
0978dc22796f722f157a36969f57f7f64bf401c7c92f4479db7a912c56550feb  openroot/bin/1167__generics.py
383fc1b291da2fd14acd9f57ae7761884b8c9e3177491209507b70bfac947df5  openroot/bin/1182__validate_call.py
93f96c564e7ba5ac4b24e701b9e1f4edcbb53a012059d541c66ea57da0b70825  openroot/bin/1185_config.py
6aea16ea5ea0d450b8d4b7223e6b08d4cea771fd344b375ef41dc2fb2bdbf662  openroot/bin/1194_pipeline.py
6bb4f0dfae94e8ade496d08235963bea773db2cfbbb86190e344d769df4eca94  openroot/bin/1195___init__.py
e444b9c56bb0d45400b3298b7b3cbc4209d5cf466955f5378e4993ef81f6ed54  openroot/bin/1199__hypothesis_plugin.py
03d557c2d465d36018fa31f40b4a2ecb954dc377e2e85fe9933b870e380000e3  openroot/bin/1207_env_settings.py
0a5f1745f0a621c544de3e40114e760bc88387c95c5fffc3de1cf68c85b1300b  openroot/bin/1214_mypy.py
d650dd5c79348cbe6e3f7bb9442600bd402518296000efb8e6592af63edfc810  openroot/bin/1218_tools.py
faa33d6d5ecf8d2405e6fc6cdfbf9e5173881706c88cf7196cd962b97f53b41c  openroot/bin/1227_http11.py
6b35f57dc9ad5da2308e9bad165678bddf7627cc708c639af5ac7d408bf8dfde  openroot/bin/1228_http2.py
6e113877d88af549b176c76c826d847ca9d76819acd9682019853eee3994ba35  openroot/bin/1236_sync.py
d8f77114cddcb34d8aa7a052a696ef9914fbabb6acade4d6e45801c44b1f941a  openroot/bin/1248__asyncio_selector_thread.py
0726547890fd6a531f7324ec791a392334ced0896d12e97f1b2abd8aa4a3a839  openroot/bin/1250__eventloop.py
39fccb3b86771e88354e78a96c89fbd9836d9286314b89475bd32a28378673cf  openroot/bin/1251__exceptions.py
ea65a1725fe919786b8195473ff4c27ccbc85c83a9f66ae810533dd1f60253f5  openroot/bin/1263___init__.py
0eb62f90d375847e94befe7fe6e2b24af0ec9e49c65437bc14229f928d15b4df  openroot/bin/1265__resources.py
9be16d138a61c5e34810b486ec0dc7ed5533de303621be49d8921ec3cf8f4baa  openroot/bin/1269__tasks.py
f5860cd805ec605bdfe0f2e3504afac91c43894781e506d8fe03a0d17fc2ea56  openroot/bin/1270__testing.py
bf7c4ab6314780d578d60d92bcc02403fa9ddadf56625088d7f94d18201ab70d  openroot/bin/1271_buffered.py
3908436ac51481fb3b4aabeabb81455c8de1a024b176bcecafe90e2ff4850390  openroot/bin/1278_sitecustomize.py
c10dbdb7c428690b2024214246f6a35c6e7f0b1f71507902d5bfdaf2a8a78ac8  openroot/bin/1280_conf.py
053c07c5d6094329eb9f98bc20eb3a5c5c4ba3d2f5120e5c8030aae986b2a6bd  openroot/bin/1282__common.py
34ca5e523ba1ffff1d3b45b35707ec6ee7e344b48e34cff71a91d2c967d4652b  openroot/bin/1293_disk_usage.py
fdfbbdb513f24b6247415fd8e679afc57b9c0b500c2ae2787115e299399c09f3  openroot/bin/1294_fans.py
03f31027177ba6f5d79ffe7bbdccde1cab861ba306544b6e60a3b958419264f8  openroot/bin/1308_sensors.py
eab7c503620396fdd8cc42a944278850c03679b5035c7e395bd6c055e5cbd844  openroot/bin/1309_temperatures.py
988483ef7b3418442921a06a1b9f224ea689e35635bba87e47e8877e91d1004c  openroot/bin/1313_bench_oneshot.py
5d79b85bb2f62aabb04b01ab4e0fa238676749a1c6acc03231f7efba655fb1da  openroot/bin/1327_print_hashes.py
032bb3056c1e28ca98174d104a671969ea0ff0c8515b9f3df20edd8b0cba7ebc  openroot/bin/1329_purge_installation.py
91f3572ec675a7e5681ad557e00b7da8c392ff337c38c54ff7279cb87116682e  openroot/bin/1335_test_bsd.py
fd301637b95d6e0a8921d87ab4c9110e2bd73e81fa4f78ca606e3bfcacc3bed1  openroot/bin/1337_test_contracts.py
0ff7ca761a7caec5c317b3ab0572d13d2ed7329a97033a89cdbae33ea94be691  openroot/bin/1348_test_windows.py
b75ada23b6762545b1f7e86e1ec0ad74faa821776a4092ec7fe2b003fe6ce529  openroot/bin/cycle_recovery_v1.py
ab698bb8da909a89f2a056e9b0f96f1e4ea40ab65842f085bdef9efb33792175  openroot/bin/faiss_search.py
d7c20749fcdc997da08df47b423cb18023ab742d23152d8b842138436c865f0b  openroot/bin/0798_agape_oracle.py
45de656a00636c4bc06d1ac1ddf7741b5ea1939a3a589fe72e4e5b41b571b8bb  openroot/bin/0800_Announce.py
c09088c3c4ceeec2a4d8f99ecc2c1dff01d3ea0a23b64eeb40d7b873b7d5e14f  openroot/bin/0805_ExampleInterface.py
642c9438500ef28d5e5242f9dccdcd0c0588d2067ce10d1c2840e008c7bb8ef0  openroot/bin/0806_Filetransfer.py
a984327d2cd6e8baf312c45cf75ea427953737c2ccdda617eb2c2c982cd9d20d  openroot/bin/0811_Request.py
9474457d8b4a6d8f29d253d1ce91b01d991957c1d0c31ab2092d34ecf1cecff0  openroot/bin/0814_Buffer.py
7fef252436d190923b5cc9b49a9a0c2971a190e502955cf8908bcc8df9bfd0b9  openroot/bin/0829_link.py
c0a89d15e63873f2786f48bc12ab984332f14bbf4f1dba51fea977d0c7c353e7  openroot/bin/0837_Provider.py
c3a4277d83fe83121af07d02875b2b6ba2a5110c909417af00e7e8e7542ada01  openroot/bin/0839_SHA256.py
d67ea8c919e9e0c6a5bc90f69be4e8fc011bd749655bb7f6482177b885522548  openroot/bin/0867_rnsd.py
f111d495ebd31ab80e21b4e0da82a0121dab342b01a23166c33546490765ba4a  openroot/bin/0871_configobj.py
6f62df0925e0c77bbb3cb987978ece57ab246a4d53d645616f5bf4a1253b4a2d  openroot/bin/0874_validate.py
089cf338614143d48bffa875b9acb3aedea15c02c70a0755851cc95ece6c0373  openroot/bin/0890_util.py
56b7324e0f34a0f25e6deada8ff002f1c186bbbd73c7b5f4651497fd9b99fa7c  openroot/bin/0896_initiator.py
d0face7b1739dba97bb1457d85e5651df5d54984c95eaa7515d6f63b2c3336ee  openroot/bin/0902_rnsh.py
17f0e62ec2cc65bf9a9671f66ea6cc4176fafc47ba318c58fa75cd5947c53eb9  openroot/bin/0906_SerialInterface.py
5576ced3fe7b8df718f08b2144b6c6e6ec9fa6163e06c45b31c9b7599ec7d01d  openroot/bin/0913_basic.py
2c9e27903ccbc04329b83905b85964aa09d3042d953b40fd150be716a0413914  openroot/bin/0933_make_unicode_wb_data.py
4227d5485a2e4619865748fe01b944e4c048b822709efb7839a4834929e0d9a5  openroot/bin/0951_upload-parakeet.py
526505319a62b8eadc8e7b8786e62260cc5e08d59faaef6406568f7f4c64e97f  openroot/bin/0965__impl.py
88ed4ace448ee36c99e9f7e0f953206f1fd9553586518d349d16045a7facde46  openroot/bin/0967___init__.py
4f8252f085eafb1d52d0b6e8da8c05f25f5fcdad8aca93b5e3b40b7b2cf8723b  openroot/bin/0983_functools.py
415fbd9a7442af6c81a61f20d35405bcdf9b43f6257bef12975dd84b274194c2  openroot/bin/0984_itertools.py
7fa87f93677be37181bfd16102784cfd8a53bd6808af3072f5c384d1e275509c  openroot/bin/0989_to_thread.py
f644ff92a0a10822544c7c30db866647f7b371d6e94585a4b03fa060dce464ff  openroot/bin/0996___init__.py
968a022a06b7fd8558bb7b3e7772fd44c3d127286c63b7e2bae1b1be4383d1cd  openroot/bin/0998__exceptions.py
28cd67deee097cb48197552e620de1a181f35c90fecaf82b9eaf2ed5c73087f0  openroot/bin/1006_alias_generators.py
cf04408d9bac391b446edc69554db4920f05a5e9b2673e05abac099359a9c184  openroot/bin/1019_functional_serializers.py
ee9fb88ef3ffffd8d9caf71d5e289d7b9a406bf26533b7c9d41824a9b8f14963  openroot/bin/1020_functional_validators.py
88742977c489e43093b4f5796ad015d3a4fcf5b8d268c15e659d8b5fd95ab196  openroot/bin/1030_tools.py
3fb7de037e4cc1370bb11d6e2fb75bd12fa8c9d071a1b9976b9e580e80606a34  openroot/bin/1033_typing.py
d799d1d90a6a4c1165415e1336d4c8b4cc93271fdf6f257e80f988118d46a287  openroot/bin/1034_utils.py
54b022e21a05a630bed5e2f41e2c5869a59a1053ba86d19c0dcb60b2a6b95482  openroot/bin/1035_validate_call_decorator.py
aff660b388c8a5c3c92ea2b975b6d26b2aa8fe254c2856b164277ea0e1f12c4b  openroot/bin/1041__api.py
640987e3b38d7e4c6bae3f8f3d88467a21e36fa0232824be00d58837838bfca6  openroot/bin/1053__urlparse.py
6527d0bfa6ab1810685a5732eb4ccad7398f1362237b48bc93329d9e8c565235  openroot/bin/1064__qs.py
6661a42204ff3eec1e772341aeb2866f1a16b64a72b49354d6e5384079e610c5  openroot/bin/1077__reflection.py
da73cecc3acf7b61800e92c244ce1b3504bc32eecb8c48821bf2c9d8000bea38  openroot/bin/1083__utils.py
b19049a7c2d081d5e2e094c3f1500d0fdea0d3e702d5aa97071c03fad9df4106  openroot/bin/1085_batches.py
b450c05a5a799e8b596e4b61d71ce89931cd8b8199de008db780526d986b4152  openroot/bin/1090_batch_cancel_response.py
2b49096248d5edd012a35a65e157a953daf5f201b7843426e5689e9cbf959dc8  openroot/bin/1101_file_delete_response.py
b25c11da067060c993a4f8a16ebd5adabaf242ec9fa9e006ce08e5b90c2598de  openroot/bin/1107___init__.py
062a870203e736b2075f332883b6a779d591b36f387fbd66cde9a7b3fe7b78ce  openroot/bin/1122_chat_completion_message.py
0a4da201299201c2e556167894cebe1f69a3c5c8e46d3294c3ece30e783df878  openroot/bin/1125_chat_completion_message_tool_call_param.py
45dce0e1d788d6e666aa09309ccacb1ef6d5d9f3d1a8a7072d0ad598a564f43c  openroot/bin/1127_chat_completion_role.py
79fef559233d1cc421210528711815254556f9b491c0adbfd4d8c5481e533e22  openroot/bin/1130_chat_completion_tool_choice_option_param.py
c5c0613d0cecc76fbd159cdbee3ea8c3040ea0ac0439fd03ddd05f83987afeed  openroot/bin/1142___init__.py
1d17e20d830fb78c101f6805807660e1cfa2dec6e5a3a6cbe464ea7044fec73f  openroot/bin/1151_asgi.py
d63aeee156c9d31eb747a76d55cb8e23e74a4130bf77f9529c9584050cc63444  openroot/bin/1158__core_utils.py
85779bfb3a1d1b04c3bc6f4e2b5ba6d7c3fae1bedca876f418e9e03f88eb81c6  openroot/bin/1164__fields.py
3e3a2051ac085e67fc2ee2cd7bdb1e26987b58b5b8309efe181b17c02b100bd4  openroot/bin/1166__generate_schema.py
efce1caaf2276f020f5abf6eb1fa57ddc87bcf8b77276b532ba374ebbff0935a  openroot/bin/1204_dataclasses.py
049b5daa2651b5abfd55114298ec6863e2889909a33f2f80fcda288e21546716  openroot/bin/1216_parse.py
6291d63902ad1a8c5fca29331ab7265c954a515601f4405da0247df784314a71  openroot/bin/1223_version.py
2c7bb8fccaf932cc109a64f7c84e282e07fd6ff2497de552e018c3c5e25ced1a  openroot/bin/1237_trio.py
cde8195bd4a7aa3dbff7dd831496bcfc2a6939506454be0083076e4644ad6a44  openroot/bin/1245_socks_proxy.py
faafb9814620febe52b0df8e61b42717f96fb56d2fe75f9d165b14f3f81db960  openroot/bin/1246__asyncio.py
10b2f68ec71a496d09c3fc40e8cb50966df1c2f144ce34db735bbd4ed7b2b742  openroot/bin/1259__tasks.py
8c4db0e7d151177c91a38be39237d917661caac059bdceba556470ac91836069  openroot/bin/1260__tempfile.py
3f8a33662927dfe0dba6861cbf28214bf14e60081b994c5ea14f3e2ffd3ba593  openroot/bin/1262__typedattr.py
3aa5984848f44e6c0bff19e2089b77fe31c55acb8c93d4c793cb424c6b0a6a92  openroot/bin/1264__eventloop.py
00e174bd209695efec6c9d46c3e086c7468423dca4e6eef46213d838f837287b  openroot/bin/1283__compat.py
0ef4f805d277e2c46956f60d3edaa8f77f3a7e4907c25629c5ac046971069794  openroot/bin/1299_meminfo.py
1d9fdb6157f00572c1ed783782ceda3f89f6c24117a5a2d59ce0b8f1b8af71bf  openroot/bin/1303_pmap.py
92b38d41a2b52648bf1a03fd81cf639e4a1d74bea679af89b540b39c08492092  openroot/bin/1319_download_wheels_github.py
80b764002692946cead27d2c2c3f1b5b229449ad43d1a48a6dad29d4ccf27e06  openroot/bin/1322_print_access_denied.py
268bd830935286edb20b7b76b1f905639b96f7a4cbecae609305e78ce476e5a4  openroot/bin/1340_test_misc.py
348e938ee5239ef0565567c8857b4b8d436ea09cc164058ffbf11570a299a829  openroot/bin/openroot_unified_launch_v1.sh
fa223437407413f15a0e8cca3a9e3754c0e5f287eefeb998f2daf66d3bf9045f  openroot/bin/pathway_chain_test.sh
86c2449d528b2eb62fb13e555e67eb112bde0838a231967e1f49ad6e21f02745  openroot/bin/resolve_pathway.sh
3cdd17ac496dc0f2de937eb155664e26a1bcf0870d02e07908076ab5e8ad3335  openroot/bin/thermal_balance_v63.py
502fccf042aae774812c8c7b08200297e002bcf1cc169071b4609f901cacf202  openroot/bin/router_relaunch_proof_v1.sh
6978d593cf204ed36fd5fe9b5e502e77649562f6291478c229e3c7105efff2c3  openroot/bin/router_relaunch_proof_v2.sh
f3a79e3281747359e03bd628c3d37f7d98167591915eb82ccdafbd499c53c1e3  openroot/bin/agape_cascade/agape_cascade_diag.py
95f2e51b125c991e76ab3fe55309ecb0d6e560b04270f7f22e61298e2aa07c74  openroot/bin/agape_cascade/agape_cascade_sim.py
68c1e950ca63f072c64429bd0901f0acedbb6575cc4f3b6749222b8dcc09b025  openroot/bin/agape_cascade/agape_cascade_v12.py
66bf1740faad26f966d16d3f33490c9f9217c4424b309d86fd7c47f72da912f1  openroot/bin/setup_restore_v1.sh
63a968d440320e4125cfc48a9a24aec0d0763d25dc461727ff2421e97461f471  openroot/bin/sync_validator.py
6a24c2751e17facb6efa5f78439adaa2e4c2c353f8fed45a934d80208d3ba6a7  openroot/bin/simple_merge.py
72e6cb1cd3fa722fa0da33160acfb9996f8a6bf0141c853a9b42e7cb470bb134  agape_one.py
758d88930be6c026be236ba98feb0d26739c841f1625ffcc315e7fa550581832  bridge.py
e87c255de46775faf9c3aa66b0446bb8cdc99d1d8a4c673221c2878eef6838d4  deep-scan-report.sh
a03d360e5151d4cbabbe578fd3a73eadd45a1ae054f2847415a8f7fd1f6cddb3  groq_max_cycles.py
580b07aa739550b0e08e74014ddddfd99b5bbd9954309a27d134620b8c48ebde  agape_clean.py
82faf6c1e2818d4db342534c54837734a2ca463e940426f34a3d49bd1c05e96a  heartbeat-status.sh
5b7dd55c81de9878fdd2c8e8794bc2903f0f1f9c3883b66a10fa3c12639dbe3d  openroot-deepdive.sh
a8f46527cc7d1e2cd86ac8fbd03f8e679423441909044fa7aeff4145a82a1132  setup_openroot_phone.sh
356b4b21977513a1a67126d2f3fd6124d950aacae32d1cf6eaf019661f9652ab  une_client.py
ade0da42e6aca3bad7a912c5965266291576ab2bbb4b7b3b2605428ec12c086b  test_une_full.py
97be438750b12233ab85bc02e01035151e3b0a3520f0a2ba1d938dc0cbe2da47  agape_slim.py
3eca98db693582faa57d1f876571538dedd3a274ae737d34d4f5b07ebe264310  launch.sh
e5c010114e3320da418cc0060d873df5968ea5d2c983fdb868c1c9740d6b3986  observe.sh
1acd7e1c0486b9769eec425272afe75786c61dff059e4ec15f6931c973c626d9  run-command.sh
3f3e6a36982d845fd5be49902b4c59224bca29615fdc28a8f67fe6c9ef2d91d2  start-volumetric-llm-node.sh
75a8aecc25390bfcb1ddf5e000ec71e542c715f622df33ccb9283d440047eb30  ghost_fix_v1.sh
72cb816bfa3a680e1a0ef5c5fa153ad4a0198d3552bbe56b02a96e74c3297fd8  wireguard.sh
ab698bb8da909a89f2a056e9b0f96f1e4ea40ab65842f085bdef9efb33792175  faiss_search.py
59590c3de85b38fe1ace0287980c08522fda3928affedb6b8552e8b5df3f0ffa  run_nomic_embed.sh
8800213d41e43f8da4c4821024bac5f2d027d25c0a487ff7fc6d9ed2e76d0e47  push_openroot_readme.sh
8d814087f2927ed2a8b4403768a295700694eed7ec57dcec6d95ed5b7cb9c1dc  push_profile_readme.sh
a351f07a2031a0158cae659d3b1d746a63e57472b7508bc5886d2e81469f37f3  push.sh
5e766c88baa87c6552cb325d5c327a0c31ec7a8671776458d64315a8b7dd552b  audit_repos.sh
4b7a677436a63aa092f6ab44b3fce0da94f39fc008ca3327cdc236c430b23973  raise_to_6n6.py
c0a128056411b3d7d121dda819f42611c32f2e984d76facbdfa0b264ec016fe6  start_llm.sh
dad4ae35e934de9bddda1c95ac4a4d96cb054f3e16679418a80aa164cdabd974  batch_nomic_embed.py
28a7bdede952f4f3ebc73d25e23fa843408fb30000df9e4887efd3e781b95511  find_original.sh
6e300e64d2222cd195bdb4f613c4cd7abe3567f491c0ee1b1ab228241ec4cda0  find-128g-usb.sh
f4c5668618dd724e5bec01f7e79050c7f697f6960059049ac026ff429ab817bb  groq_fallback.py
1ac6674a1300bf94cd194531ddaf4d61329053ffde9967fd597dc1b6f8bd8658  phone_check.sh
81533c8e3eed23f6d9b4c4d5bd52a14f62127dda6a472c2e60eea937daf114cd  one_principle_n_power_n.py
0cd3a6176896cf7c009240268d71d9256e713141d5e0f5264f29aae5635cfd94  newton_chain.py
c41aea80e79e9f05e731276d5b823ce94773301408d918bbe3cfea92bb355f11  local_rag_search.py
80bdef56a6cae1efbcffec9813516f63e05098e3045793a85be66df4f8407541  agape_hierarchical_raising.py
8600f822418cae4f86cf749ba56756bd7f0c6f56ec42e78445085f2c94bd5e0f  lattice_cli.py
40a12947f9c37a0685dd12cdf6c89b8106347a8e948e5d2af816a2ba4280e65f  portfolio-audit.sh
bfc5e9063fbbbb8af06f89ef2a32553205990e9af21f07ef83ed5187cc5d5303  openroot_launch.sh
c3fadb58f0e6b6b7ba971e8776da05b944d7d9c45a8281fd8bb0eacac0b61757  openroot_full.sh
661989674dd1d99bcac00e4a68e0bede89c6ced3ce0ffba6f09a43ed96f3b862  openroot_fix.sh
58e38f0c3bd5a94ede3b73180e11938cd12ddc515b5b34d8245454f7897094b8  deepdive.sh
c3384926ce5fbf01b4db2e3c9918b5efa9f5f5f47723dde447bbbb1ada4033b9  fix-secrets.sh
bcc91476ddea747810e4b10e43b47b322af37f2470e9da81af0a2b6bc9ce480c  fix-license.sh
96b91c7a6fcd3feee0450d5c34bdbed67472426783a92ed041de493b669cfe80  stack.sh
1223fdb34b8707037579124e05811c55032e69ee274f6d3a58b76721d5eae4c2  run_rampup.sh
148483f4ab20640d46346dac23a642473639b26a67357461ebcaa0ac373c0886  push-openroot.sh
d6303f2256a3174a0532d51685393226427bb52893167d81109ea1e1199b48f3  openroot.py
1ceaf592f02be2a0b3fc4320e526ccfaee951c2f3b651b1544300b78d9063024  mdpipe.py
0611ca8f58b176e7e767ed987dff501db69633b855c9483d97cab7dd9c92ef49  diagnostic_check.sh
1fa5e746d67c9d14efd5c55b8030f95fe30d53d34cdb259b84a0716f4307f7f5  test_phone_tasks.py
a34f0d53c536ea6ef56826bb50203543b836e960ce811a86bf0f43a0b0a8c162  enhance_tasks_with_efficiency.py
d05393f651b7a8fec7cbf190a657092572e97654bee9fd012e71cd3c490915c8  fix.sh
9c6467bd6591b73ebc8ca5d23c5508c7868773c7593485c7b4ecddd23b1e5aeb  start_full_embed.sh
efb822288c2d94b8dd8f22104080a593c260fcad22559ef3efa3465900d774ae  bootstrap-node.sh
3f32c316cb2b9d913a79394da9a0996baffe03dc844c4c4d17591ff27e1a7f48  repo_audit.sh
99df48d3864898b22669080a9e8ee6c17f642e9a11ee3c87753011d31f60168e  .une-save.sh
6ac1e3781502105d99e6dbfffc91cd9b1cc725ebf8b7a05024cb4586176c5726  phase1_audit.sh
89db87f53665bdebfd8595bf424e0cb349d4cbd285e9a314d6597bde268a23bb  apply_fs_hook.py
894505648c39c9166e59fb3e91cc2800c7c1968f1c1e09577ca2c9e9db2a382a  fs_hook_patch.py
d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed  openroot_deploy.sh
9a63d9c013a3d06a34dc20c8670c28de867d6e49fc94d9a804afc119cd4c339f  agape_init.py
588a96b244af79fc57a2f62d7a4845ba429fdca617a8b8828a48c09ffd721115  cleanup_and_backup.sh
9b67c65247fa651e21d299d08ee2cc475b7ef95b3e4f7fade696cb7cbf964ea8  constitutive_voice_engine.py
b380ad0bdb7f3c3b89d2e0751d74bb4eb38f76d75e9d14ab6c0ecf983009a54d  openroot_claude_pointer.sh
9642f2a93c46cd9c7e562a4411cfae51fd27bb0acb40e6c7a0d64ad7a39269b4  constitutive_compiler.py
6f3629a6dd6b74b61c41b5b286e67bf8293e80093314eb07687fadbd1d5dc649  fix_chain_verify.py
971f6d638bdf99314515acc3f686acdfb249172fb0d87f54208c1e6a005290d9  openroot_hub.py
bc1234dfe2c73080681886d2f12d6648aa1f2af9356c2cbf78ae1dade8c7cf4a  agape_frequency.py
c2bccfd9e316e5a1526ad7c08267e290eecfdf00ad5df7fbdc6f26b08e3daacd  agape_neurogenic_kernel.py
636c14f66d1d89090818df9b9b0c91a4c7263db5b3d78ca07388e1acb8c81394  agape_setup.sh
a85ec9624641134dbcd38bca8fd4c45cd78e212cfb3e6b575fec2e4d6dbc9db4  filescraper.sh
a36fce85f9dc35024a5221c88163eff4b7b0a4a3d6741aaa58cf59285dc03a9d  agape_evolution_v2.py
221e3008d121d314ae45451034de9878701149fae6c8bb670f3d0ff39a99277a  openroot_archiver.py
77667a63c4f6f743b902958329644a60ad4c4d24334b1b809e83e53aac7d1c67  unified_agape_engine.py
c23b8545407dd7f7a491eb226e9b0f0b13de9b5fcf6f8b003496cbdea63436b0  relay_probe_v2.sh
85577b88c546a8482b0f4f43c99e256ac50e417f243dd0775be23a4151ceeb6c  relay_v3.sh
a970a00e32936cd77f62dac8ffecd33081c5bb9f25195429c1db61de89868e8c  relay_arm_v7.sh
6e518f904159575e4787a29a68ef6bbc8d13ab3b952623978687b4ea792e1eb4  repair_une_syntax.py
613c1d85aff1671b9136924085c3066db4370049cfe28a5d8001b2f0c2f877f4  fix_une_and_commit.sh
0f773d5de57d3585ca1db00167481fd8d57cbb5d4fef4b996fdfb0314732a250  commit_une_syntax_clean.sh
b18250dacd94dd2ed1184e042f4eca5d549ec7080394a5dbc0dc16db147f301e  repair_all_une_and_commit.py
2fbac0244f5dfffe94bb2aeb0ab8970ed7585face7fbfcc9fb46b0fc7ce05161  emergency_fix_all.sh
a8f4807391b85eaf9c72fb7ee2fb576e1690953cbc5e3e03b5842e567b78f43a  openroot_unify.py
5171887db6ebb8da5909fff2261ad03ea61a1210fad6c3785ed296baac94a539  compressor_node.py
37921a8779cd1c963572fbd17ab75782ca999ea96bd274e25b67d53c021d4327  core_engine.py
e2f1963a7b58efcf8fcf75689b7a2b213ccd06b19dac7f1dbfcd05bd047f780a  fix_last_une_error.py
4897854d1974f180f6dbad94823aa3809750de8135aa28d8963af6b8273a4e0c  ride_along_v1.sh
803aa501638aa1733ed3cb44719e4ea58429413211c75d47bbe9501edce37b53  hive_swarm.py
6fbcd043a3951016242f9faf20273d853a37cbfcac1922cd0e1fc22296abc867  apape_net_setup.py
a848c74f05700c7f0b7355d8ca91aa6c8143569136fc902e4c5048813f2a9cdd  map_files.py
fbfb274e8fdee0e092f3d5b633dae8bcd91231b3f5c1c1728dc3ef9dda98df51  inspect_map.py
08cf6f8ee69e0e5165508c54092aacea13d621325c751542fe01d16e689fb163  build_coder_environment.py
abdd87ab69226068a64eca2e558d4f6f29f15fa1292a8168fdd43e437f2eae05  v7.py
5f243b0c65c9797d847adf2c37dee9a6f21a8ac8fb1035669775b3e6fb5c9385  swarm_bench.py
a9741944411f24bedb89bd3bcbaa5311ceb57cf23dad88946f0977a1bbd20d07  smoke_fix.py
6af9b798dffd3652b76ed26ac3310a0b0d9b61497f03fb13e8dd04b6ef591e61  post_launch_triage.sh
468e6fc3407c0eca5d2bdc1bf179f1edb36f4b63031ba5f1f3bb6f9a059c58c3  triage_followup.sh
dc123856567d1fc459d60db81798628d493387db91800cbf36eaf6dc2160aae4  vault_status.sh
a0afc43213ab4dc43b8b7971f6d553137fca80d57c4086b014652f9a807f1936  openroot_termux_recovery.sh
85a722fc429be7c3cc119a8eb9b0328635e29bf660129b525156a1e25dd3429a  openroot_branch_resolution.sh
cf1fb1226aae22ea6ca9bfbb29a08d8f517abe547de23d9ce5fb5f2af1cddfa7  issue_triage_v1.sh
c64b8bca47bf51fbc5c1b2b5b06a65b3cfde7ccd07d3e514ead2451bf8aa3d9f  dup_cleanup_v1.sh
9493d45f1c04c909c5ab689d93f13edeba3ac1db5264eb64cdd346ec68186d0d  forge_rename_fix_v6.sh
c0733f530c0f0426589ed76726f5648ba95bac873d3a3d55c019be444522f0b3  or_docrefresh_v1.sh
26ecce72f422232bcf96105f33ea31fd816b5465f2b18033e013689eb9733c2e  kai_extract_v2.sh
16b6267d10aeee2a8926618647d236de9136be64ac47ecc1a433799f2bc15950  lumo_courier_v1.sh
17e527a4ad3674b71e81145256331d047bb02be6557570a82fe3a139451ddffe  hash_assign_v1.sh
e7d2999e6a44100cc60f1ec841a80d4c29da711fdaa8d81ddd070b838be06b42  A1.py
332e96002153daa2de5a9bb0f36100ec8edcff6c9e1b982db24898d169bea27a  hash_manifest.py
2121ac2af666f20bf70956e79085d8aede1213c18880a3c512bb87cd105e4c65  relay_report_v9.sh
d7d3c6ce4161412901adc2e68b303d509c4af8ecbdb44917ddd437aab148f405  relay_roundtrip_v11.sh
d041ff0f4afd415a96bc73988f3e64ac9390b6e1dd1dc68450cde78452f60576  relay_package_v15.sh
5d0ea6cc523e800ef465190d920a7a9fdf3027a2f89a555657c83dcc667a34a6  relay_autonomy_probe_v18.sh
86e9e8563d62a8b86d4a3b4b7e29d2ccc8ee916a67f49e2e37f9552f2597367c  relay_autobank_v22.sh
caa7ea6f76f6e493dd54113ac053714a204ecaff9d5426aa43658effafa09c9b  relay_autobank_v23.sh
fbcefea1a532acba68fb3ff843541d7b48c82ffcaffbe28b20e07d3017b5307f  openroot_credit_tracker.sh
03f58acb668a55c82a6744f5babb2cc7bc6f281dd230c30fa2cf541b0c523204  openroot_finance_tracker.sh
1cff1ad9ca8f2b4a012a798af5330abd8bdc0bfa4fd44db51bb639b561b1b408  scheduler.sh
e13d128e1493158a1526d4103b00a5ad10035aed4505b153ff7e2058511eb5d9  find_api_keys.sh
30d0c1a8cda7b594e97e2f44d5aab84a6e89164ff43be50ed9e027225c9bd261  joule_leverage_analyzer.py
e7f32e365721f5c4c1c8337f87cf59e5ca86f4836bedaeb75a3915eeea245040  snapshot_bootstrap.py
5615f936bedfbb6a3e4bc3f26ee58a2c832a9fe445a84b861340fb5c63c1fc45  backup_to_usb.sh
7a4b6fffb5daf37595245d446223edea80b07dbd2f8ce53ff35b7b3f5acadd7f  patch_voice.py
d3e2f5dde73db76b6471419945162dafa5b7c1f48aee374e3b7ee88c386a4d6d  termux-hygiene.sh
d871e9c40bf9c9ce3c469182b806e3d018919fc127ef5bf26bccd37337a2197c  agape_farm_os.py
88ce4853e5e3a9e0097f9e42c46c22c727f83ef6899486def4be4e528210bcbe  une_max_efficiency_lang.py
39b6b32c60f144b1f3bc7f0da71e30c51344d0345c97ab771b7849ebbff2152e  une_atomic_library.py
7fdb388236ebf03c2c0d113667045a9b68d42027799c4d7a11484b2832162052  sacred_geometry_agape.py
c54cd37678a16457d4d5b342537c52c95f5575fb75a557bf7ced61519acf6d75  agape_kernel_v2.py
e169e8f6f177d8627ee44d141402aa121e47ffed34611bde5880874a32299271  agape_ledger_chain.py
77f7fa9d5756f196b0fa28ecf0ae66c0e859a951ff0041dad8a7d46f94908314  und_protocol.py
fdc87757b7da44b0f1de597b558227630615b203de220f14ab9cb702122b16b1  agape_node_bootstrap.py
0070c19cfb50608838864e9dec62a4e6634740f1bc51e09e8686afe0e3f2dbb7  agape_primitive_forge.py
1d0afc39207ab7fa2310d075f65be4c07aba90e298e322a301ff22b8dd83ca25  une_closed_loop.sh
d0084794a9dd43d675c5c63054272a3fbc11ae2a1acfbf8031dc6ddc4def784b  final_une_syntax_pass.py
f15c10dda22e30f267e225768e07b05d6ad6e2e7dbace67ea73276d222096b85  emergency_syntax_fix.py
0f954dc6f30d6b3ac1230cb276ec32271069c70a78ba0e84ba31219ac6fbe644  diagnose_and_fix.py
009e74507c85695b8b068853efbc8b96b61b186d4dbc26a340b709dcdde7ca6f  diag_fix.py
7796f195362ef873813b90835110159fafcd51fb2f36038336e70e23f7418f62  surgical_fix.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  final_fix.py
2de1ed86e6006da242b87221b8230b57dca58558bbd3ce3c3c8b45b5f1e882b8  fix_final.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  fix_exact.py
307eb605bb8dde8de6f94b4e8f9b576a3a1e2c23a4f53fd7290608182efa5504  agapenet_unified_setup.py
36ddfe7c5bb34941cebf24d8522d9d1321c233ddfc2d852d054960e951ea41ed  storage_daemon.py
67b05a3c3c94dad5b22ac969624a9885df700e752dad075f2a6f1e34f564afe4  fast_backup_daemon.py
3716cadbe304d415aa8c830e2ada43ce03c29a94b84bc9c6c37af0a2c8456b51  agape_net_setup.py
ac42da68fa8d315d42ca570720c64c83948b0357dfd20f5878018f21c67be154  agape_net_full_integration.py
f6a5b53d586699ec4a4b3b84713ae1d1d78f56f53dac8e8af4a3f55a77932588  openroot_thesis_one_shot.sh
42ca14270b8471ed9dc8645802603c93bdb308531337c45f85d9e9afe56c29a0  index_content_blobs.py
0ad0e4d40e08f8a2e6032f049dd08412111058bd0f06ca6b1c3e52c0b82128c1  une_fix.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  fix_kai.sh
191a22b35206447d93f848c3c2243cc5be06f1e6ebe9b45de7b2f892e6445ce9  usb_flash_import.sh
927c1c2d34c3d39c5557376bc1b17854af3be0e55ee8b93d8efb6f52a65cf2db  openroot_tailscale_ssh.sh
df451f704f27e0069de9bd15cd22e628a3002325d9b4715fffba2638324fc34a  orchestrate_team.py
44f6f8c17dac192e8fcfe230c72fb9a4344219cbf0c18ca310437c48476a239c  repo_hygiene_gate.sh
035fa34f33972c1c8db09dd4b740eaf60d8145801760c067cf3397120e09762c  ts_check.sh
5a519f42138e33bfca43f8a96c8f3c64416189eb1b0e320009137e92ddb801fb  update_goals_final.sh
60a580e464c65dc0434d4c0dc5aabff512aa7039bceeab479823b58c2181071d  forge_run_a15_v2.sh
eed620102b18ad89eda4f225afc4da19975c638e5161a14816689335894ddfa3  forge_fix_base_v3.sh
bdbe8969b7b1e4affb430dc65bda15f05a54c8da452cf494b9e18d3f7bf4f818  forge_targets_fix_v4.sh
2b70149a03c987d8dc87043160ebe9a4093c4ffa5939f77697a216af95f1fa01  forge_full_ship_v5.sh
54d5308546a896664fddd3e11d953cd08a80404a130018ca8a533374651de75b  setup_this.sh
84bc425c9bdc212b7581edb043f2a91491197ac54d3b36e006ffa4e198102872  kai_extract_v1.sh
9130bebc2e6a72168c461bb7f0780b87592ad4e9768619ae24441ee93d862c08  ride_along_v2.sh
546bdb6c955158ace52209cd6bb00b67dfbf41c3bad245cfcba24ab3d52d2728  phi4_router_v1.sh
68a8fb1c8a2c7d767f3c26d76f142c881dd2ac8ab407ebfd261e57d2b6cb037c  seed_to_markor_v1.sh
8c05b904ac781a776de919628d247328c6d72c9d5d73026fecf3725361e933b8  orbundle_stage2_compose_v2.sh
95d0a32b87653733d6b8867e5f729dd39d73316eb4c550998116847d96ea3472  orbundle_stage7_finalize_v2.sh
d1f351b5c51f41835baf5627d3af00b3f646f579b1856408531a7b0c995b2e28  finish_loop_v2.sh
99609708744cee5dcff347be8ccd789c23a85429f81ba2e26f50a8978a7ec3ab  agape_thermo_merge_v1.sh
2371a706278a5caac0a540dff6444bcb5cd16be611246527759d48652006b0b9  joules_counter_v1.sh
7d2f384a0cddd19afc6641651deba2dc1a9e5ce2a2d54a3cd13f8204d604dd08  consolidate_state_v1.sh
70efcbf1bad84567d7a94237fa32fd17b16005b3687c748d1bbf005a47c79ed3  complete_arc_v1.sh
e7338a18f689b30b60186ce5aa07900acbd699b2b0286a55c719319d8b228798  openroot_replay_gate_source_v1.sh
5498e3bd88af6cb426cedf30d9770493f5a8ae4f1faedc0e187944547a09fddc  openroot_extract_audit_only_v1.sh
a4b81d3e2298513933ccda877240f24a453cc1b7b008a19cfb11f288e7219a10  openroot_double_cache_probe_v1.sh
82b481b8cccbff4375fce582c81bf467a93824388c09181e88204e53ec28f74a  openroot_preserved_pair_replay_v1.sh
62265a85d15e99ef9b86986e66e7dffb50c9cee81f020d6589d7b3ff1cbbb330  openroot_commit_experiment_snapshot_v1.sh
d1302a0de09edbbe641b77823f616350b57e9f0e8d0f99eb41ec9580f8fb3225  openroot_github_intake_compat_v2.sh
56d62a53a296e6a984412559c4c5738437b56450fe3b27e0d8269d918685ea6f  openroot_intake_reseal_rerank_v3.sh
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  openroot_intake_deliver_v4.sh
b92e553c0febcfcbd929b9e6509f3dc40f0c43fd09bb65fd62eb74ff1a58961d  agape_multilingual_drift_matrix_v1.sh
464e56e0e7a16a68dc90a013b1593c0f28de1ed61dcab72533b8224828f26640  check_ancient_source_words_v1.sh
f71c519c92d4441ac093216adc1423620bb08e4dd31f0418bafa31f3a2930fd0  life_giving_ancient_roots_v1.sh
b895eebda13f389543bc51c6afa90e94e137cafac2a2fa8c511774cfd8ef365e  grep_symbols_v1.sh
bfe654ea2e2f4fdc28b7aac7acb8b87c472f9200a6099b5679676a64db3afe2e  fix_loader_type_v1.sh
adea95ee4ffead0bbc649f8e8c2e5a7ed63f02ff09ef85794139dd79b86f7370  push_and_emit_seed_v1.sh
59298d5c1d78675514767a2bcfe6fd973cdff5d425863fa6ece419fde5870654  cross_window_reconcile_v1.py
8320ac3fa7f5b5ed02e8e1bd8d0c48bde33f5e6fe17968acd29f5fa4bac6bd23  gh_branch_audit_v1.py
3ebc6240402151d725e19c5e61fa629daadd2bf582ab040da223df89157c25b9  gh_branch_review_v1.py
8f0de55a012a76cba528a6588fe3c3a0e5dad15269bbebe88bc164d5fdb3fd43  rk1.sh
50514e49471108f70ffc6db69921f0230a985d8ecacdfea06acd168b02f29790  rk_final.sh
f56ae3e432c675d27496bd9e1eb0f283cc4ecb61041e37b72707a60d9555ce41  rk_push.sh
4441e3101ec1a0045dc8eb7949b9dc16cc65627f57fd2d12d3615c40fafa2987  compost_lookup.sh
b0c085c720c71a2ef1163c46d39a3aec21df6606c40bc5f61c2311cdd434ae13  nomad_recon.sh
d3ab0519d74d703b181570555c8ed90676ccedd7b0d487bd3a81371a7be10061  nomad_recon2.sh
e394af178e5d23c607c56b5da93b58c497fc9105f349146dcb912caf9d21209f  nomad_build.sh
30c0ff94cc74fcc5b672c6746f3677c19f84f13982c1eb44646ef2e462a7892c  nomad_fix2.sh
cfb4ec793725a79ece8cb66decdbfce7b9333eefd710934035e51fe536f06711  disk_truth.sh
50c44862d78d838bd43f759fe1247bdf029377651a9ab54ea38bef8d9f55dd1a  eta_audit.sh
ff8ce1c55e2a05787ab53b33254ed785a76cc1a4ac6a4e42afb03cb8c6237605  eta_gamma_finalize.sh
db52ae85379a5d963175ded3921ce777bf7d70b396a5c9219bd034d83a216e2e  gamma_direction_fix.sh
391e68c5c4eca035a06ad91e5da44a2beedcdaf4561d1c9698fa19baff015b19  openroot_promote_acre_ledger_v1.sh
5433f4cc2b44188d5847f8002b30be56777ee1c4d21b2e053aa23d626db30c20  openroot_acre_bak_diag_v1.sh
d7044d6e616a8347784dd8ea0d0d227538eb13ecc146356c9f8c72758c7b9b24  openroot_full_coverage_fix_v2.sh
dd6062d6224e567594aaae63f0d974ed66658ba0ded0be0b00dbf3939e0e7622  openroot_harvest_gate_v1.sh
a95762c1eb7895dc4b699e01475cf5fcb02cecf07b97de7d0b0253ca2eae5122  openroot_nomad_delete_v1.sh
0e2938b05f32002ebea70fe475eb79e0e8517778fb1407ec53e51272e221692a  emit_window_seed_v2_fixed.sh
c751a1e1d64afb70551f0ab5edb314d077b7f5041ad807764c678c1ff5bfd06c  openroot_partial_hunter_v1.sh
ae9f73e3d900ed5d994627b7d0b91e4ea065d0aff11705355d3fce3c9b65ba7d  openroot_treasure_recon_v2.sh
09bbe3b0691ca1172cb130a1a1c15a27b5c8571183b61fd180db24baa52ac8c9  openroot_watchdog_and_sweep_v1.sh
0d8ba7c2c9689bdc054027c29b5828b89a041b4e6d7b7243766bc8121591a6be  openroot_partial_ledger_census_v1.sh
9e98bb41861db2d6d29f57301abe3d8dbd5a5ceea38d18b1bce122ceb2927318  qh_v1.py
bf8fabf3ea6aa55af951dd22188ce7b7db393a6a22c7b52104fdef5dc292c518  openroot_newton_resolve_v2.sh
67e62f7bdd34ffdb42b6e37f8e5530c984c2dc89b7f613a46ba062d2dc1f4c47  openroot_pod_data_inject_coder_v3.sh
b6ccd58873a80e35d896d94cab9d9a9761fd1587d787298ae1cbc95c58485e50  openroot_docsearch_gt_coder_v2.sh
317b949368db8c89cd4535e7e3cc908815c090c3c5f40f0041a053ffcfc3a9dd  event_seal_and_scan_status_v1.sh
3a7786712dd9cea5af2cf53732fed3587ac610d57e2cd271998acde700f55550  ledger_ssd_backup_v1.sh
f3479074c79cf670f52a7e58cd79bf26a9c5a8c006525602321e961a053dfa00  unified_final_merge_v1.sh
45c33c271dbfe330ca86f3afd876f850b0d24752293bf07ba11b9fac43311cde  unified_evidence_800k_builder_v1.py
87c5bf6b8f60d493f91b8e6e8a94d9622187e86dab2fc303b207e4a175224e85  openroot_unified_evidence_800k_v2.sh
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  openroot_unified_evidence_800k_v3.sh
7a7845ba63bbdd1a5a0311c5ce11b165d23ef5a1adbfd463e0e0965316e176b3  unified_evidence_builder_v3.py
65eb21f3507e332b46f3a390c0279f09af9cfc351a33f25ca6e5c1189cb389ad  openroot_import_a15_v1.sh
af4daf62cddfd6c5948b3289cf18b77bc20bda277fe943f7a5b60996dd0f8f43  openroot_command_ledger.py
eacd18a083fc3e6ef96cdab7a3153a346ed7ba2102a318c66a61b872e9e57690  bg_process_check_v1.sh
2707810544dfe95661a2cc8b86e0d256e3eacac5bed152fae773adea3632f843  audit_recent_commits_v1.sh
59f6468fb96aa8d92d6fc149c1d6591c6b9687de32d5e97d59284d39fc55c16c  word_census_v1.py
33844ca17b3f02df87affc5759f1de8ffc25be6983fa23392a195a187fee8ba0  pod_garden_bootstrap_v2.sh
d9a81750b7384eeb6a18a34164f9907805ae75412047258eb87b7cd1808de13f  openroot_garden_repair_dilute_v1.sh
637ee36cc10176380c98dbf5a3f8df27f8a878806975c07ad5296e9b7e34a478  pod_per_repo_clean_build_v4.sh
c5c822173dcd04d34aea57213e201c763ed6e023b920b93cf53d7e1252504538  mesh_zone_fix_v2.sh
5621309d2111ab0a214eb9723af121d4a49779a7a7fba683d5408b33c91344db  mesh_dossier_engine_v1.sh
44c73c5c679e7d36413135719a8b0592ef0a3e174d19e5e437e22b3b2cc2d80d  router_gb_install_v1.sh
aa854aa3a4c1ab1ced70452b107a3f125379a3d80abec8931acee1b66be09816  router_gb_install_v2.sh
d93d979786e0cce0771acc33299f7e3f4c86dbf43c1f3eccd31d6a037e11bd0d  router_gb_install_v4.sh
3faff6ebe4cb907657af6486b20e82e079a08d5e24c5ca5dbd9ae0b67e25863e  router_benchmark_gate_v1.sh
8cf704cc36bb8d03a62f4fa9511989068d91da383864f5ed38bd409cb6734bdb  router_gate_run_v2.sh
1c4eae86fe954ea17de0d199ac81189dc8c6d1f1f5fc5b3cb2614687b3075433  recover_v1.sh
fca27ec5801b9bdaba6ba54e97daabe4c8472ec014227c202d4165a4abe00627  find_recent_ai_loop.py
2fc0d2a48b0ee19ba46dde6a8c6ae7ca9c23c8d23e60061df63010ec1cfb7507  deploy_to_jesse.sh
d240b7e1abedc60fff2f047f8d9db9bae95add316953c1c3674e4b0e5579d732  relay_resume_v5.sh
4b60570f084a6307648e70f4507e229bad119dd78f393fd370b42cd1e01b1298  relay_acceptance_v13.sh
c50e77158801f6215f83f89652e833dcb93128e5a64f0c842dbdd047a693579b  relay_finalize_v17.sh
6abdff8035884cf2233107f48ef846b80c1ef443356b5ded23d4527b86efc8ac  relay_report_bank_v19.sh
8cc26d179cdc2ad00a6eadf8cbdb224ac89f71238e31eba7ca5685971b58cfac  relay_report_bank_v21.sh
f5f055b66151f1f135115112ff76f4e33ccb5ed2a86848d466cb3deb6d7cd3bf  embed_patch_v1.sh
3a2b4e063c551c8d31758509d429ead0b15dacf0a8b650a1f9a4eaea38a7c370  merkle_lineage_v1.sh
7e1579521b49ae3189cbca28382a04fe717eba43ee4247e037c1b24712caf7a9  emit_window_seed_v1.sh
33ebfeff9fc6a356dc6fc018ac97b6ec1b0a5618c468921297e951aa35f8017d  orbundle_stage6_guide_v2.sh
751c14631f0c29cf342aedbeba8bc264c010ecb9af0aa9c1c7376d201068571a  agape_stage1_genesis.sh
27ad992abe2073c2f2f054a7e050ed227009c19c57c30cbfa0467d89aa238f81  agape_stage2_run.sh
3e4136780072ae927f160d751f84af224a4f073805049c97ee1db24bfec0f7fd  create_query_wrapper_v1.sh
6de2526ff939b2a973e678c91025f9c8415e689933705315b02607e86b490041  fix_merge_v2_rebuild.sh
974928b81e93f3e3bd19f293ff69525bb7db5d4bf54cd984860b65b3d79bfc0c  inject_joules_badge_v1.sh
7782259b9f2abc5c800ee8e38987ce1987b82c66c020b16b92d103a1e0132cec  joules_badge_multi_repo_v1.sh
1a741213ddfccd6df2a58a402f8b7cdf039759c0c473710132cf211028dab85a  nomenclature_seed_v1.sh
484a2c3ce00d8ab6d6ad22acb8decf5c665381867113062e54fc5975ba157c30  check_bash_history_v1.sh
4803b78911ef2012a579d879ad5f4acbe9bcdacd3bab2afdae8c11508e0a2a9b  openroot_recovery_search_v1.sh
b7c5fbf2f255bec025f5b9790ff7d769d578a7fb4025af54c030fa68791ddb3f  openroot_core_manifest_v1.sh
19710462324b535d8099e21f3b1a1b86e64acc3ce2bb5a1e1a7217ab2f42783b  openroot_energy_core_contract_v1.sh
9703f13c7dcb4467a19eca4adbbc8a7f3819e42f7cbc3c25ae774e73c0ca8dab  openroot_commit_scope_v1.sh
2934f3a674322dee1230f05d46e2982fd8717117fd7b700a6e7ea388e1a1b334  openroot_main_sync_gate_v1.sh
e47a25a1fd8fbf2a6e08a84f8d19bcbe35367f0516f2e9d27f571aad28f2529a  openroot_existing_index_intake_plan_v1.sh
d3dd107d38841bd2c4c4fa43748695b3f0b99890d2e898ccb2052bea8cfbd72a  generate_nomenclature.py
f3c99067eaf6d0b15f2951b40ed397ceffe1149ee9a7be958ad5587fdc1cf7e0  patch_euclid_loader_v1.sh
909c259f62a279f9c5a4202a26643eb93c9887e5fd7604687763f846a3bd95a5  grand_unification_loop_v1.sh
3a6dc1baea3ff2a6f36fbaab51af3935a278563a3454f4c1a58e593aad06d180  run_unification_proper.sh
8fe3925f84528f35b7f50f5d24d9dbf72921f1cd6e625ef81f1764acfd477b00  save_and_verify_seed_v1.sh
dd7f4ba3cc38630e4b55dc7ec2eae87f292f220a8771a9f743e78481aaf1eee3  emit_full_seed_v2.sh
cdeda57098f6792037eac32732b51fa76cbe343a482ca863ec871cc9a4ea1a9d  final_sync_check_v1.sh
f252b5e32291f5a5ff1388b8de9b737b0ab5042d20217e53ab93128878318d57  eta_executor_batch_v1.py
916d485acef4e1681a764196da18b1cfa778bdba0af0363da0581de36b99de3f  eta_executor_correction_v1.py
f9a03894bbd019aa987e35486896d610a4f460b27373fa2b971dd399bee1befc  gh_branch_final_v1.py
9b367602a69c93de0f444881430855800b5f62783c72da7202345a10b391d962  lost_file_restore_v1.sh
83c886af6a014880e1cc37a85f9b0074f8b07c234449cfe4259a818ce026ca02  rk2.sh
17de76fff84a4cda0b3e810a7512a4cdf4ad1136c1832b7e5c0aa35a4193884f  rk4.sh
22acccca31bb9b9cd39392c829b555b36d209079012a6fe1d2bc9b6659f639d7  rk6.sh
2dc79381c45b8f222665ae7e43085ad8cb8b8b004805ce917273c6004e0b6e3a  mistake_restore.sh
61e0acbf2d05a29c1b64b11defcd9c9fd96e6ea7988737757c6b6447b8155ef3  eta_dump.sh
e5ee334d04c359c3870336ddecd17f8a2bbd70f4859184f13da0aa36c58c49e5  eta_commit_push.sh
d2c34abfb0d6b8203ab64ab0e56646eb8cb458bdaa90cc2c6c68ff21103d4dad  openroot_agape_acre_inspect_v1.sh
282c216227254294b0b5ed9b819ae4f8310fd190c1450d6d8589b402dbf06703  openroot_acre_v2_canon_v2.sh
87d591084314c508d25d6272c61d93f4b5ca56084c54fb148d0499995d33a0c1  openroot_a15_hash_audit_v1.sh
0c3e15f9fd75d9460d0c738561c61af474c25359782f7d2a37d2208fc6de555c  openroot_cross_device_final_scan_v1.sh
f6d75e727750397539c2c6a4926ecaf99998620ebba5877b7a81879642422e61  openroot_update_state_pods_v2.sh
540199d78ff7b1719eea0348a8b973779351508886231e36192c32c28ed7bbd9  openroot_update_state_doctrine_v3.sh
51ebab9c01ee4c3b05265962483dd359b2b7f4d1e962b43b2081e6b46ad6af38  openroot_update_state_doctrine_v4.sh
665418908e92e3d13215cd91ee0d250e04a60a439234e421d1db508dace8b86a  openroot_nomad_cleanup_root_owned_v1.sh
c9a57bcad09cd0df0c186855c627ab318143900247ecaae840901b2a2d87aa71  openroot_partial_ledger_census_v2.sh
8ab643a36226d8dad1cab593222c80b1faea558d3ce928f6da4d28d4e823d19a  openroot_tri_status_v1.sh
1a69e39ed5241c3fe600df5514805efd615d2e2b869acae18a756367196a4242  openroot_census_inspect_v1.sh
237ea0f8b87b9de416b4545e95146c881df49e3f9c3106e98f1272b201ed2674  ask_pod_v1.py
3f61377546fd293a021c1e2c99abc25a04ed6daeb8a7aad09d18dc0a4d758b16  openroot_pod_era_v1_ship_v1.sh
71976569d3ef728782fb361360b22c51ea09affac46b553f254c6f322f3751ef  openroot_safe_handoff_v1.sh
9bec43b22666e9d28cc1489033aada83a26416439e6ee19c82d33d577e062958  ghost_script_audit_v1.sh
cea83f30e38d7119946a5e84c991fd57e2f33e0157d0939750c6ecbff5d8b7d4  ghost_recon_v1.sh
2a52717cb2383b81091c53c4536201ebb8ef2f092dd1168c223bd6816739dce9  ghost_commit_v1.sh
020e068f56b88c1d542b90818fe280fdd9b157ef8eafe45cd657f7f1ac54bb28  openroot_ultimate_plan_persist_v1.sh
c8fff3c23623860c912c21f18989fd075ab0236ac8663d5085d9b0779f5fe549  openroot_interaction_access_seed_v1.sh
2360850c180aa001e2fcc8ffa5833905c6475e3471ad47aa1d58a3682f290052  openroot_evidence_reconcile_v1.sh
57b1e6aa82c4bbd95747481f1efd324356732701d358ce752a6a1d49234f6c6d  openroot_bank_768k_receipt_v1.sh
8b8232ac1b836a6b16fa75eedc9fdc36bf1dd68866984c1befe18d36ab7d1b7a  openroot_pod_skill_v1.py
b655d76e1fa4a6bd6cf01757794852c2454d2e11b849f1a4f79f0f24f0ef54f1  find_gh_docs_pod_v1.sh
9d032aff862ee76d0af5f8ccf1da248d8ae30ee3921a3296e8cd3600ab827e44  seal_audit_debris_v1.sh
5890ba54fee6abb006f0dbc8799b2de14ecbda6a1fc386aecfbb13ec99dc62c0  pod_garden_bootstrap_v3.sh
d793662f97a5533fa8af880eaf9b275bea3ae2ea7c4ded08df34b55d1a347691  dossier_snippet_and_seal_fix_v2.sh
4580b2bcd7432083308f34113f308d4ce9de90862db4f332b2d1c92afee4afce  dossier_kw_compile_v5_ship.sh
b5cd3ebae0cd3d98640185314a7dc0cf98b2d5e9207c0d5145fe1c61af78f15f  pod_per_repo_fix_v2.sh
b5d77dd4d899d2928fdea00b6c6ed49744464a376ba7078dc011952b55e81c1a  smart_router_test_v1.sh
b7cc10b8975511106d879c66d27364b4591025caed2cd148d325c38f4d623cb9  mesh_dossier_fix_v3.sh
dcf5ab1442bd1c2d70b84ca1194ff59239f0c6f0e11e87c654f373078d1cb240  router_gb_install_v5.sh
91b0ef744161274c7100a450713b58ba4ea2bde5bb12199187146af69ba26754  openroot_alligator_trace_v1.sh
ddb882ef2432c463dbdc04f20d895ccd7bae82715161c373ab66aa20e3792073  fix_selfchurn_v1.sh
19c5304798e4903a38cfd0bd3301e83543355597ac5919a502293417765e7845  commit_state_hash_patch_v1.sh
2d0569eb7dd946b515b9422017b2cc7e799a7ac2bb6ec5ddb58d4b2c7d1b8636  handoff_seal_v1.sh
db8f5b4456196b4c1eb6c295a494e9470bc36a64c2011b9a283aeba5ed343810  save_script_protocol.sh
0423749271300c559ff218f6b16ac86903513eb8bb0f3e73ec5f93e1909489f2  orbundle_stage3_setup_v2.sh
69459fd33322344d64afe9a85fbf8e8d126730ee3106edeff6b169502c417b6e  stage_commit_push_all_v1.sh
c84518ed40dbea3a44ebd5a8987b6a124607a62327a2debbf25d6762eff34e0a  queue_update_v1.sh
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  agape_genesis_v1.sh
1a2e62bac42eadb377d5f0da3c3cdfa576095cb218f9087ea16e604c537a850d  fix_bridge_format_v1.sh
d8c324147ee975592508b9f5020d22ee7b0c30dd0e622077e7cc16532b3cf90e  instrument_self_accounting_v1.sh
bc5049d546a34cabc3ad42b03a6a3f33ca8f8aa085dbd970ea6c2510afac2152  agape_thermo_merge_v2.sh
77b9b2ba4eea3509e02caa2053ba7232f207afd48c08fd1764b0866ce24db4a0  governance_seed_v1.sh
b20eb6a62d1a6e6237101091eec57508d10e7bf36fa85e7650d358474abfcabf  gh_cache_rapl_v1.sh
e0a0448be670003b8f48848817ae1d5ed680673165c1f9eba924818ebbb328d1  openroot_core_contract_extract_v1.sh
1bc88d050805a362aa2ae4a540725190d159f14b89cc682fe6dbac20dbca13e4  openroot_miss_summary_v1.sh
985635c9c1bbb1f567d0f16aa0fdd2cbdd11296d1a4a01ac5f1cf0aba8592307  openroot_rights_energy_gate_v1.sh
d4c0b37afcb9dc2ea37c8110e911df8c57ccf11ed25f78ff0cf2c381a201c519  openroot_reconcile_handoff_v1.sh
127b5b0ccca68df2297d78ba6b9116d1f0d27d8a82fb990ddbb81cfbd122e514  openroot_finish_closure_v2.sh
1870f4b2c7aa1137f697bf5c53f7405f3f7462760ec8e772164d7b05f5359ddb  openroot_intake_deliver_v5.sh
de544997fc5f94600d6d0a2ae76af540000f329bcd4ee268c65693ff5f520a2d  openroot_intake_promotion_contract_v1.sh
87f4021b07d81cd26727a595c49ee4a99f31d5ce6338920b9d942da26d85299f  openroot_apply_index_plan_v1.sh
e503a8739d35d08a6036dec8313581bfa2e6efb0f633774418a2a3cd3aae24a2  check_nasb_resonance_v1.sh
2c0d58094b5648b9aa6db1ba918d5e33d993a76eb5d2db687e057f21874c0e00  find_postulates_json_v1.sh
51d0934c56087d2c2d06d8c0b7017cca2cbc7424f33d0eb09418765d229d82d4  deploy_engines_v7_safe.sh
e040b83fb9ae63f9a46d1fd05b12d69070150b0c6233ef90965fc0891a3388ff  test_engines_v7.sh
4a72dcdbcb4ab8451f1cb005e72517c4a731178677c8bd228f14264b81f03640  agape_nomenclature_v1.sh
f0dee0afb450c39253dbcef6fe8703e2e51ae1427e9d40a75f1615fda893b439  block_1_nomenclature.sh
5b65e456d15283bec2e57b500616d4e0d4aed2663bf5617be2885f7215052b2c  commit_and_push_loop_v1.sh
d0700484ae4386c32161510965839650d3e639470de8dceb44c5649142dcd95f  embed_agape_universe_v1.sh
93a0b2e2de936b0ec5b1e0092f66ef38bf20c8e47870209d82f25ebf682ccbd5  git_audit_v1.sh
a020dd9438d792410bd1690c9697149eb7ceb91f7d82f2c52d4a138b03a12b22  eta_rank_engine_v1.py
86db55a64b8cb6b8ba28d626055515b32463a67c6912ffefb951550fb81e3ff0  gh_survey_cached_v1.py
7ee2876adf49d385d5d810c103a6bd2e721cf8fee00e9e97fb90f98baf90b4e8  gh_branch_diag_v1.py
ed65c4d1e24d67288c4ab0a52fe625f4402c35b8423529f8a8da3ccc7610951b  gh_lost_work_recovery_v1.py
01f5bf9a405ff723d1d3c322db2828d2076b8e951c8fa59fb57001cd2bf573a6  rk5.sh
360133fb382a93c149495e7d887033a22a5e27dbf4e77e4750e5b58912c191c8  mistake_rescue.sh
b4d7975c0269d382e80ceec118873828f174dd8ba788ba169c545c65576f324a  mistake_dump.sh
1f2d3687750e18dbc2b4372d2cd8a6a1f4ed2ef18b6fb3540742ae38fcd7d016  mk_ci2.sh
86f601e9a0c3b96ea6ce122772a666a445092c55ff28d7d4dbeb73493fbc2ee7  close_session.sh
f6f35c6b4387547ab4cf165c2d98878acf93aad9f2e38568a8bdc4926d4982e3  nomad_fix_and_verify.sh
ac3c5e3e4af5357a9cc3a2d52b3951bd84d52d2423090e16ddc9f5243dce26fa  eta_fix.sh
da50b6615285d12b17aac4d44049f9af3b9ccb84dc11a1ae758d0064fa92bd41  openroot_acre_ledger_repair_v1.sh
aa5c404ecdeb017996fd3ac1a4cee98d450c6aafc652d665a101cee254c9d7ab  openroot_acre_ledger_repair_v2.sh
9fafb0c0fcda9ea40a36bb6d32bf79cb55bf253a0206b95708bff241e92d1097  openroot_acre_recipe_probe_v1.sh
9b37ce414aa1ae6a54818d872eb49d7a54648f2723986d7c0cdf3e84b1887047  openroot_acre_final_repair_v1.sh
b71be639c5904a986eb8a05f00bf1cc4d202c581189b139f47d3f965c1ec5ce7  openroot_acre_fix_dest_v1.sh
2e14423a22e358e1f8d77de847f372ea131bac92ea965f95f5be8b24f7503dd8  openroot_acre_value_audit_v1.sh
d8ec5e167af20421b31b1ff1f397d69a8206d9cc33ebc68c1da8725428df04b6  openroot_eta_gamma_cinema_v1.sh
a2a7a8e0bbc4615fc4bf4aba053624e0826b8bee8b0c9a704627e6db9904f045  openroot_acre_v2_canon_v1.sh
633b970ddd41b22c891280161d886ef5526b1f05afc6cbaf75e770e36531826d  openroot_a15_hash_universe_v1.sh
b6304502dad8cba790e3a755cd230c34532365b4d17565af5e50fe7015bca30e  openroot_index_census_v1.sh
0ae27d21285c3fc75f08f148eaefeff44b24fcf99eb7719b1bfd5ddb5eaf7b8c  openroot_nomad_mysql_probe_v1.sh
dceea7b7f3669f028a6df0f0a5f927bac18afd351e6679ed07af568842c3c113  openroot_treasure_recon_v3.sh
563c3a61745e00958726ed570d14f7396d941b4298734017623e19fbaca31585  openroot_pod_launch_v1.sh
bfb98f79a13f6f385b6436da0a5c1dfe96975ed79956c28160943c6d629036fa  openroot_census_resume_v3.sh
bd082d1cca53003e980ab8098118e02f0716f0cba22ba8155bce65097d570554  openroot_pod_resume_v3.sh
da47952d72d7eb5834249ed2667de2934bd4e4bf40ffc2a5fa043cec027dd884  openroot_overnight_v1.sh
66ef93f6ab9431d1c9fd7826e1a063a799770ff83b7d1f5b805ba6c585a7503b  validate_newton_append_v2.py
89c7446007dd8ff3cefbdbcfef11b8bcd08e4deddd328992403802d2ac4625eb  openroot_pod_era_v1_finish_v1.sh
21b21bba2914972b35cba072dff0c9c3ff44d22c61bfe21346e81144a9e4d5dd  openroot_pod_era_v1_finish_v3.sh
f5f15e13c14a680d4821815478d710198a1afbfd558856997e32a1fb96740dcc  openroot_unblock_and_coder_docsearch_v1.sh
b69cd04eb8c62d54402a99ca45ec4b176ceee9452f987a79ea8dfff414cfcb97  openroot_surgical_model_ingest_v1.sh
6d62a89a656d8094db73f58b3630fba7f4f6199c2923842b831b97167940099a  openroot_safe_handoff_v2.sh
d105044912f3bddb58a1536439853d45fa5cd18dd86ce57f5351fd44384dc32a  unified_clone_merge_v2.sh
26ea18d9f336db44b58f29c561ae687caa9472cac635847b165dfb491a8b52c4  a15_shared_corpus_v1.sh
a978523900840ddc925934597f33b2850f3c6620c273b1c68bd3c8b1ea7c4127  openroot_readme_commons_draft_v1.sh
9b274e36a727e280b1f0a808ecfa3632e6217b09fdb29b02848f254291842041  unified_ledger_profile_v1.py
ce481bbd6bcecb3c44840d8125fa3a35fd23a6e8a455b36c2f32e82aca0d0fd0  unified_ledger_builder_v2.py
89c51a84b00861cf77fff66a62f68d5122598b1910d671adad666c6669760ded  openroot_filemap_inventory_v1.sh
eaa2e0c6ab8d5008b689ffc6f263190990f1b9b063295345871b39a07349a9bc  import_a15_into_unified_v1.py
04b998b45fad031862ba1c6e9121c626d684a7d1d58517c87164d6765d72c5aa  openroot_session_mega_v1.sh
5a01d3087b91c73ce513155a98e38796d37066ec68685b1fe9163a19aeeebf8d  openroot_stack_tiered_bench_v1.sh
2a220c624a3647d9690c2e2682a732c68a9b8e75109cfc797e453d7b0ee90df9  dossier_kw_full_v1.py
5676c3935d7e91af39079b803e176f374fe6185dd16f697c3dc11e72aff71bc3  dossier_kw_full_v2.py
89df177eb624dc1982a50812b433f9bc4c0074c3c2d031546ee9908c59119586  dossier_kw_full_v3.py
63a229ca1084026bdb888adcac29188b20c8eca8937517dbe42060e32469f8f4  pod_garden_bootstrap_v1.sh
541c8e56d815f722045d6e4c7d261357e3417765481198e549274146a3f21d47  pod_tier_spine_v1.sh
1e92fb20f073758a859831e02ea5018f5ca2a0520133eb2431e46af545a5c6b7  dossier_recon_and_fix_v1.sh
6f288953ef81ba45af6d136be2a6f92dce965eb38c5c8144e9c3963d5bd7c314  pod_per_repo_fix_local_v3.sh
45eb80d95e5e245dd3f0fb6390d49d33a691e1aa7b31ff36d02f48197da7472a  pod_per_repo_build_v2.sh
bd1c8a09ff4c8b8a0cf94fd2fc6dc70580e48cae58a5d6bb86a6aa915b1fc0b0  micro_model_fleet_v1.sh
71be4f0f364f7d0980a37729f23286a48f421dd6d1d0f393cf3c74289447fa1e  mesh_zone_gateway_v1.sh
211f9b5332a0f22401ee591db8da5b94716d369b75b81d0ec65d1b6b7607a369  heartbeat_mesh_integration_v1.sh
ee3958a1765e875c1d3a22f5b1a9135c434ebda1fbdd943dbbf126dab9b05c8c  router_gb_install_v3.sh
8ef81b7eb1ab71afe88bf235d39dbcf9af5c357f202c4042d20a2742fff457e9  openroot_loop_question_receipt_v1.sh
6947d2546816e51817899b45da861510347234fc938eb1f1e1ebeb4107859ae7  deploy_to_jesse_robust.sh
cb375c1583b1207e253590fcc447766f4dfbda83f4f4d0c1c73b5af429add8b1  relay_verify_v6.sh
e2ba316bf339df87710128e693d850e2962e74a592cdcfd8101ad5d30070fe36  relay_release_probe_v14.sh
af350601ae05de3234b95af7d7b5f1f2f19dc3970be0f463202d8bb7e2c210d5  relay_reconcile_v16.sh
49217f1b85615d1acf927f76b5463ecb765382d0a36bfe5037e2bcbe734f77ba  relay_report_bank_v20.sh
cb28b5c25a8ae2abd0e440c1ab874082730726442179ecac4395e2be654a8763  semantic_routing_v1.sh
cb6a913058d6b3658d4f163c1b43e4260bc7e08bc9d4ad817613202488810cc4  backup_emitter_to_repo_v1.sh
e99dc72d98bb7fcd91485da83cab3a38763a101a9e2c5ed43f738660525536c3  orbundle_stage1_dockerfile_v2.sh
c1d58a093f6efe8bcc3f031df1cebe4647f25f230ce87102e09245afd4254cdd  orbundle_stage4_readme_v2.sh
b9a22f4e0e9dfd5157ec0e59fa9d62f904a203a3ccf890e0cd2fc72cfada2b82  orbundle_stage5_index_v2.sh
7183711254b36d0ada65e611dc24de848c69d8be379ce0b3cb057ed2341375f6  fix_agape_merge_v2.sh
d636aa8d14b8b8a758853459e91d59c21c370cf74a4eee094e45598d4da63de1  fix_merge_and_create_v1.sh
7ec75d0da8829849150f466ecbcd8169ee00588e55d58f76007287f4894f4f52  nomenclature_trials_v1.sh
f41d3508f2c61b7f1b4ff6d571b06628c90948f804de72131a1ce1f3a336e4f2  a_definition_resonance_v1.sh
1e8be2a2bd02024802333e2feac0f44fa5efbd4d417e5573b1ddc55f88cad081  a_definition_multilang_v1.sh
3af7e1edfb58e86f4d4c5d979269f3aaeb81dc717db113b211bc4158d6d93a58  verify_loop_metrics_v1.sh
cdc0ac2cd4a58b363685ddc9d05742e8c7dca7097ee22af519c9e7115e83f75a  fix_pathways_schema_v1.sh
c8bcc44e186e803e5874abf0b66768b74b60ad0f04d16dcf51e572778efa126d  trace_history_v1.sh
f539cb1ba43f6ad3c3ebde22205b5b6cff68581adb9c28aa376fe3641a3e7d84  inspect_window_seed_v1.sh
70211bcf81d14bcf9ccca83289dced0b2a0d8338265b55f2ab70de5becc0da51  resonance_nasb_multilang_v1.sh
6a8c83482c1533cd9cd642ac1a604bf755172a3e96177abd8c352dd5456c9b2a  openroot_baseline_inspect_v1.sh
fb36310f9812f6a1ffc6f71fcc29ac7b42a7c7b8d9631d8656639d382a84fb76  openroot_today_phi_receipts_v1.sh
6c2cd7eb9b62c2551415f7717daf59a9a6cdcbda78f2820ad0fcfa5371c6df32  openroot_audit_baseline_contract_v1.sh
b60ab5be1c3bc86ba43e8c6388770547ead67639b87e21d095d12d0d89983fa3  openroot_cache_miss_diagnosis_v1.sh
089fd5dfa5d41bae3f9492d39428627691a14391756b50ebf885819c27ee2170  openroot_close_recovery_loop_v1.sh
6f96b0e55972f42666c0c48284d61ae26d7d3e64ed66eb929b4c3531a9b23309  openroot_commit_push_closure_v3.sh
6936871ed91a1553d5a0bbdf66b21d3ac44882d7667bcd0c2463f7914c9f4b6d  openroot_github_intake_rank_v1.sh
d7d0dbdb65c2da6131d2e5f6faece51282c652b47e3c191d741c02b4efac67f8  openroot_existing_index_writer_contract_v1.sh
8ebe77016e26aaa398bf2306bdb72853949282f3ec24f1ee54828e24091552b8  nasb_kjv_agape_drift_v1.sh
04d61f41757df4bcf166a7142701b42267e1530b1c6972aa358a8939e6fa3490  bootstrap_agape_kb_v1.sh
d3aa0b9ede59c8dcc0860f2f9d2072e59ecaf543c5f2ea094559635854d0650f  test_euclid_loader_v1.sh
e0547c0e91588bebe8d9bb52141992337f46456ee6510dc1ddcc18db2954a11c  deploy_engines_v7.sh
4905044b0bcf5e0c2332267b5f1b484eeb5529c4acd64372671fd2e3c3198ed9  agape_dense_nomenclature_v2.sh
a9325326dd5293b2676dca17b26250a16dfec409dcf5a6f7cdfd42a2221f4f2f  fix_loader_robust_v2.sh
2b9a958d0c6a88f0148fc6d2eadc915557137d9704cefdd9d8bb9ac184294091  block_2_geometry.sh
6405c008ecf97df91f2803c47c8f61820091904487ce2119e3db4cb523161449  block_3_seal.sh
abc0e5c348ac09ac2afbe4c7e80c565cea816a62c5b3e805b95507a1d2c545a0  test_full_pipeline_v1.sh
375f6d0f260352921ca67ecb9b39293eec33247827199f835d904039cae067d7  complete_convergence_seal_v1.sh
526b02355c0bfc17c7ff429dcab99c7f566b40fcaf545eb0ba98a2238919355f  embed_agape_universe_v2.sh
e59bb45d17306d8a3fd6724b5e117bb40c8867617c10008d3623cab708e6e16a  rk3.sh
e96d21bdf1e7e5885179b6a9e290ec4f31103cd798107c1cae0961dcd7a08f81  stage_and_commit_audit_v1.sh
50e95d3d3875ec0600312e13846df363a9e155e12b811022efde0da67c224c70  push_and_sync_all_v1.sh
f815682081ab135df16c70356216cb71e516a987f6b4ac4dac7c49c08de44945  pull_and_push_une_v1.sh
dcdfe77abe938d8d1259a6b9d823fab7d1aa4dad4025d8037906355af6ba8c6f  rebase_reconcile_v1.sh
cabc1c235f178c240dbd3482c5c63e122e57d1ccfc63d190c76efe41c9ef1760  compost_inspect.sh
4585028c4169f350344e3b5a75e259508d2f5c1211884107e3488d997d74ed59  nomad_integration_analysis.sh
54d207b400e2da3ba8fffcfd83d78de3b105bc4b1f1525826fe85c154505997a  nomad_inventory.sh
1953854dc7a9901d7e22edb4e417115015ecc076464abb6e24ada11e94def6d4  nomad_recon3.sh
53484133481021612cbb211870e7e7f0fc8a4585616fb2fd328614bbbe2f19ec  admin_diag.sh
b3349d8196e71403e2e8996dfe1dda971891967be05722cd68c22f686fa0d41b  gamma_audit.sh
351718b370c23d35ecf0e642b8d5d8cfa404ba5b7ac1eb6670fbe96d283fa900  eta_gamma_search.sh
77739045fdb959d834d439f9e4d4a3644286480159703aac2e4d8a2d2988ecf9  gamma_deep.sh
add618e30db91d17425e9193de45e36f9d9450dda997109c63b0526e3d31681d  eta_gamma_complete.sh
b34cb9ec8c681026c2cce5dd1454bbee3fee122bf3c3e6eb469fbff36f9ae0e2  eta_gamma_fix_branch.sh
8aff5d02a6fe9f631c481d554ea74724a0f8ee6468f18047a699ad1ce210f2c8  openroot_agape_acre_lookup_v1.sh
ec47c43fd30c54f3ed1f5531b68ade6df3dfc78bf1cafa5a4b53f319accbfb81  openroot_acre_chain_verify_v1.sh
6e9f87f0e544179622b332d3dcc845e866b0eea5a35a9450b1d227fcb9b18e30  openroot_acre_forensic_v1.sh
eb3fa99006402a1dcdb17053b93e91024f219f4919a59049abb717ef467c4645  openroot_acre_verify_commit_v1.sh
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  openroot_full_coverage_fix_v1.sh
d3f8bd09e4849a02e92260055dd42ebdb135240a21cc52110b134247558a6263  openroot_a15_hash_audit_v2.py
f47493e759fbfcbbc113047a3f5e2e9c51cef69b6e45ed5c4a06178973dd2271  openroot_update_state_pods_v1.sh
149122d763ffa382e8f6dd2e3ab3ad8aac3f3fdcf5f2a97dd9b782c88374786a  openroot_hidden_work_hunt_v1.sh
4a911bcfaf2ae2671371a7e55c567daaf43ebca643b7f26375d2b5c60eedd441  openroot_nomad_delete_v2.sh
0990217c4fb9d244f2eded0b059c7d0f674b7665c1ee24dc5bacf95b89c9ab73  openroot_nomad_cleanup_root_owned_v2.sh
f10d46a5331421c0a90425d7fc8c118b92ad4fa012e02c5236e86a374eca5776  emit_window_seed_v2.sh
f68d11a2e31202aff08ebce4f75c1d78364bec60da0b43933f7baca333a3a4f4  openroot_treasure_recon_v1.sh
ab83b17c7533cd38f0711af94eb3bd7258e91e2aa0b3d21b5f5a3cbd38b231bf  openroot_pod_builder_v2.sh
ca190288577b43cb503b57dc41d9bdfcc2f2b60391c5eec54ef31e76c7e48cf0  openroot_pod_flock_v4.sh
748d8254d2f4ef322ef13648b9cca80594ad0898e4cfe9484e259a233bc00e0b  openroot_census_inspect_v2.sh
29238e4e23f31e730d7aa07273ec2c8cc029fffd05e8b6731387a58caa5d9780  openroot_query_harness_v1.sh
d24707d3f36ac7e07bc1dbed264d0c51106499ce6ef293cbe43b177dc03acfb6  openroot_gh_announce_v1.sh
e62dbd3eafbcb73b8d10b6e18595612744d317ddec7882597a088c1a77476641  openroot_newton_resolve_v1.sh
576b2fdddf91b090b76bba9921a653a49ce6af25a00bf339bd6c1a508e400a01  validate_newton_append.py
ca342be68108aadb35432bfbd8e413764f672505f89afd0b5725f0cfe4224258  openroot_pod_era_v1_finish_v2.sh
627a02e10708a7339870c902e2cc6496ce46502687d46955de08871c3747a57e  openroot_surgical_model_ingest_v2.sh
8f2fda2ec8a4f7617d0079039d2e6d00a6129e8755e989ba383e92a29fe889dc  full_ledger_audit_backup_v1.sh
1c1b2fe6772af7e94ea185800e0909ae62131b5e085d8f80599f61e10c263c14  unified_ledger_merge_v1.sh
8a398bcbb8b7ea3bb6cd4a5d5c31bab28ec689c1da5648a78aa86c1900081182  openroot_unified_ledger_merge_plan_v1.sh
7cc9515fb05cada080c24a0413b8fb87a0ffc8bbb93335c5dd1caa2e5c551d2c  openroot_unified_ledger_v1.sh
afaab83c601a33b08eb1f8279939917956712a10b6a77b9d72b7d916efe5bc57  unified_ledger_builder_v1.py
555a001bf2b298810e1ac15a3b8584625fd6a0f0ce5484d33b7265dad2b008b3  openroot_unified_ledger_v2.sh
248024500662c2c1d394e81471815f3673a9a53b1554e7249efa130f199a5ce4  openroot_unified_evidence_800k_v1.sh
33c0b6c7a782be3dc91bf6458c6075db75651d946ce0f498d5fcd8c5bfca044b  unified_evidence_builder_v2.py
02a339809d194ad027cd511a0cab109c5f29d5f20749f495d098ff3849784d07  openroot_commit_architecture_drafts_v1.sh
650241e9c67c4c1fefb491f2f867d1030fd7b046e8bb02577bdb99b156c6eaa4  openroot_a15_ledger_inventory_v1.sh
06b9a4cbe5cb1b88d528af81ad57c579474d3c5c6798e0e8adcc5591b3b7fed2  openroot_local_model_command_ledger_v1.sh
c47e0f2044ba683b5c550570274a61b6681645017228cc26125d195edf4b8d41  superloop_quarantine_diag_v1.sh
e3644fc98606f710b327a5fcf608d7fb7e99bc021c714eefd663f1309676e3b2  word_census_v2.py
cbb61f8208364ba0e0148c22192806902f0c7679926fe3ca12343e35c0a99147  census_and_coder_v1.sh
cc0074d95667fed09650d7f9f354e7ed4e3d20cfe3a7b548c524996e6863f376  pod_chunk_hash_upgrade_v1.sh
37fc833a63f11bc9593cb06a79e52b2a4f780da4acb19fdafcb4e59c8ef21efd  pod_per_repo_build_v1.sh
cbeffc8efe224db3a80df26e21b2c6a82e152ec32ae6b171bb9b725e1027f66c  mesh_dossier_prove_v2.sh
6e31c9ceafc74da7d39980483ddef0f0bcab429eec97d9afd270ac97c94cd168  openroot_pod_init_v1.sh
f97a4ca4db92e6e3c0a731b3707c749430d8acb9b3ab740557d4c5b00a724a32  rollout.sh
65d571bf547f0327d924549a1055c237f55b90c02131a6ea0559ebef144b0a9d  bg_process_check_v2.sh
c5d5e54b44c4a5b09d3d26ea7e3db06a0c1b05d9ac545150dd2ab4df910f3ced  terminal_forensics_v1.sh
ea2287818f446561c0756007d8b6c16c69e7b46daf3a6f8b475299a81c5ffeee  dossier_kw_compile_v4_ship.sh
25dcf9eb44f7971be545209082c5dd2d63a8d35be6595e246debaf654ab22fce  dossier_kw_compile_v4_1_ship.sh
2a58dbac6839f22a1ca18969fd29ae84bd41efb23359037b4a2c02eb21349f22  pod_per_repo_fix_local_v2.sh
3be3fa48152958bf3a68663738fe66013a61ab9472f5e430814eb19d5facb9e3  openroot_receipt_install_v1.sh
b72059813c3147cc8f38fd7b28ff40834386ef299500291c1cf3068331c7555a  install_openroot_query_v1.sh
df4958de8f97d8cb1a33de8e8513f792a4afa26e34a73081563eaeeef8704048  bin/pplx_relay_v1.sh
ba0caad7110f1463fc80c39195086084e5b3b187edd2fd85b5088bb49f0f05dd  bin/pod
d0f42fdbae73a26c1eb9dd1f3d979d90686f9bb4ff44379964104d3465b4775f  .local/bin/httpx
a11543bf7f916034caa70325fa563525394f0c61cb0b2c33e5b517f027bcc6df  .local/bin/openroot-query
0c519ed32e9756f68112246d1199db733f85f4eae90ae608bc2cf1155a2099db  openroot/bin/goals_rebuild_v1_20260920.py
024de654f4cf2b29ecc987e5d52f02f4a2d0b2d5d88c6f730fc638454372a637  openroot/bin/goals_rebuild_v2_20260920.py
2d8ec439c6be73a971f25171319bdd7d1a359d20ede0f27227d2482b66117bac  openroot/bin/goals_rebuild_v3_20260920.py
719d63fbb844bfd1e671388199967aad046fe90c5d9d34cebd1ee2f20b231af2  openroot/bin/todo_processor.py
a8d9a42732ad9d24f54265b85ace046d304f96360a655171213ed7fa2a3775eb  openroot/bin/onepass_v3.sh
9b6c72b529d3b50e6b252edb72854220c35944267ed5a3fd6c363e5c5eb75b79  openroot/bin/push_guard.py
73718d8799cf89365e8878c799708d752aa3925b3d6d568499fea4cc39f80570  openroot/bin/stack_gate.sh
847a017f26d74df5729da759bfa82b153d1c5364a4ac145c4dc23277fe14c1e1  openroot/bin/packet_query_v1.py
018a573b8ff7ef9e337ee5c44246e1eb03d169b5eb1cb0407842bf69d6df0ce1  openroot/bin/find_green777.py
871e0b0f69fb16ed327b7757f595b9f0963367e8dee65a954af4f9cfa19eb755  master_codebase_orchestrator.py
OPENROOT_EOF

case "$MODE" in
  verify)
    scp -q "$WORK/manifest.sha256" "$TARGET:/tmp/openroot-manifest.sha256"
    ssh "$TARGET" "cd '$DST_ROOT' && sha256sum -c /tmp/openroot-manifest.sha256 --quiet" \
      && echo "✔ verification passed — target matches manifest (2148 files)"
    exit 0
    ;;
esac

RSYNC_OPTS=(-a --checksum --files-from="$WORK/files.txt" --info=progress2)
if [ "$MODE" = "dry" ]; then
  RSYNC_OPTS+=(--dry-run --itemize-changes)
  echo "→ DRY RUN · rsync 2148 files  $SRC_ROOT/ → $TARGET:$DST_ROOT/"
else
  echo "→ APPLY · rsync 2148 files  $SRC_ROOT/ → $TARGET:$DST_ROOT/"
fi
rsync "${RSYNC_OPTS[@]}" "$SRC_ROOT"/ "$TARGET:$DST_ROOT"/

echo "→ verifying hashes on $TARGET"
scp -q "$WORK/manifest.sha256" "$TARGET:/tmp/openroot-manifest.sha256"
ssh "$TARGET" "cd '$DST_ROOT' && sha256sum -c /tmp/openroot-manifest.sha256 --quiet" \
  && echo "✔ rollout verified — 2148 files match the SHA-256 manifest"

# ── Manual symlink checklist (19) ─────────────────────────────────
#   bin/hive  ->  /data/data/com.termux/files/home/bin/hive_entry.py
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' 'bin/hive'
#   bin/openroot-copilot-prompt  ->  /data/data/com.termux/files/home/openroot/.github/copilot-instructions.md
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' 'bin/openroot-copilot-prompt'
#   bin/termics_clipboard_to_master.py  ->  /sdcard/openroot/bin/termics_clipboard_to_master.py
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' 'bin/termics_clipboard_to_master.py'
#   bin/termics_float.py  ->  /sdcard/openroot/bin/termics_float.py
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' 'bin/termics_float.py'
#   bin/termics-run-last  ->  /sdcard/openroot/bin/termics-run-last
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' 'bin/termics-run-last'
#   bin/termics-bridge  ->  /sdcard/openroot/bin/termics-bridge
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' 'bin/termics-bridge'
#   .local/bin/or-biz  ->  /data/data/com.termux/files/home/openroot/bin/or-biz
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-biz'
#   .local/bin/or  ->  /data/data/com.termux/files/home/openroot/bin/or
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or'
#   .local/bin/or-manifest  ->  /data/data/com.termux/files/home/openroot/bin/or-manifest
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-manifest'
#   .local/bin/conv-archaeologist  ->  /data/data/com.termux/files/home/openroot/bin/conv-archaeologist
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/conv-archaeologist'
#   .local/bin/kai  ->  /data/data/com.termux/files/home/openroot/bin/kai
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/kai'
#   .local/bin/scatter-map  ->  /data/data/com.termux/files/home/openroot/bin/scatter-map
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/scatter-map'
#   .local/bin/or-status  ->  /data/data/com.termux/files/home/bin/or-status
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-status'
#   .local/bin/or-sync  ->  /data/data/com.termux/files/home/bin/or-sync
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-sync'
#   .local/bin/or-syncthing  ->  /data/data/com.termux/files/home/bin/or-syncthing
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-syncthing'
#   .local/bin/or-oracle  ->  /data/data/com.termux/files/home/bin/or-oracle
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-oracle'
#   .local/bin/or-learn  ->  /data/data/com.termux/files/home/bin/or-learn
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-learn'
#   .local/bin/or-nodes  ->  /data/data/com.termux/files/home/bin/or-nodes
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-nodes'
#   .local/bin/or-resume  ->  /data/data/com.termux/files/home/bin/or-resume
#     # recreate on $TARGET if needed:
#     # ln -sfn '<target on $TARGET>' '.local/bin/or-resume'

echo "done ($MODE) · workdir cleaned"

