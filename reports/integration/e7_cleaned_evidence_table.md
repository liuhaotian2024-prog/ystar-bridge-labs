# E7 Cleaned Evidence Table

| Source ID | Domain | Opportunity IDs | Role | Claim Type | Customer-Facing Usable | Limitations |
| --- | --- | --- | --- | --- | --- | --- |
| e6_source_seeded_public_page_read_source_001_e6_mcp_security_001 | modelcontextprotocol.io | opp_regulatory_security_mcp_boundary | trust_gap | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit pricing/billin |
| e6_source_seeded_public_page_read_source_002_e6_mcp_tools_002 | modelcontextprotocol.io | opp_regulatory_security_mcp_boundary | trust_gap | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit pricing/billin |
| e6_source_seeded_public_page_read_source_003_e6_github_copilot_plans_003 | github.com | opp_budget_governance_audit, opp_open_source_paid_support | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit trust/governan |
| e6_source_seeded_public_page_read_source_004_e6_github_copilot_enterprise_billing_004 | docs.github.com | opp_budget_governance_audit | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; Vendor pricing pages are b |
| e6_source_seeded_public_page_read_source_005_e6_langsmith_pricing_006 | www.langchain.com | opp_integration_implementation_ai_ops_room, opp_external_pain_agent_bottleneck | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit trust/governan |
| e6_source_seeded_public_page_read_source_006_e6_crewai_pricing_007 | www.crewai.com | opp_integration_implementation_ai_ops_room, opp_support_subscription_agent_onboarding | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit trust/governan |
| e6_source_seeded_public_page_read_source_007_e6_zapier_pricing_008 | zapier.com | opp_integration_implementation_ai_ops_room, opp_content_distribution_diagnostic_funnel | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit trust/governan |
| e6_source_seeded_public_page_read_source_008_e6_humanloop_pricing_009 | humanloop.com | opp_internal_asset_founder_audit, opp_integration_implementation_ai_ops_room | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; Vendor pricing pages are b |
| e6_source_seeded_public_page_read_source_009_e6_incident_io_pricing_011 | incident.io | opp_competition_gap_incident_postmortem | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; Vendor pricing pages are b |
| e6_source_seeded_public_page_read_source_010_e6_rootly_pricing_012 | rootly.com | opp_competition_gap_incident_postmortem | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; Vendor pricing pages are b |
| e6_source_seeded_public_page_read_source_011_e6_github_sponsors_013 | github.com | opp_open_source_paid_support, opp_low_burden_template_support | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit trust/governan |
| e6_source_seeded_public_page_read_source_012_e6_aws_genai_partners_015 | aws.amazon.com | opp_partner_channel_enablement, opp_integration_implementation_ai_ops_room | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit pricing/billin |
| e6_source_seeded_public_page_read_source_013_e6_retool_pricing_017 | retool.com | opp_integration_implementation_ai_ops_room, opp_content_distribution_diagnostic_funnel | pricing_budget | inferred_from_source | False | Signals are deterministic excerpts from public page text only.; No customer contact; login; form submission; payment; or publication occurred.; Source interpretation requires owner review before any external use.; No explicit trust/governan |

## Cleaned Signals
### e6_source_seeded_public_page_read_source_001_e6_mcp_security_001
- cleaned_buyer_pain_signal: Security Best Practices - Model Context Protocol modelcontextprotocol.io public docs Security Best Practices - Model Context Protocol
- cleaned_pricing_budget_signal: none
- cleaned_competitor_substitute_signal: ces - Model Context Protocol modelcontextprotocol.io public docs Security Best Practices - Model Context Protocol
- cleaned_buying_process_signal: none
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_002_e6_mcp_tools_002
- cleaned_buyer_pain_signal: Seed sought tool invocation model, human-in-the-loop, approval boundary, security considerations; excerpt requires human review.
- cleaned_pricing_budget_signal: none
- cleaned_competitor_substitute_signal: modelcontextprotocol.io is a public incumbent/source in category `public docs`. ols - Model Context Protocol modelcontextprotocol.io public docs Tools - Model Context Protocol
- cleaned_buying_process_signal: none
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_003_e6_github_copilot_plans_003
- cleaned_buyer_pain_signal: lling_ui_visibility","actions_image_version_event","actions_workflow_language_service_allow_concurrency_queue","agent_conflict_resolution","alternate_user_config_repo","arianotify_comprehensive_migration","billing_discount_threshold_notific
- cleaned_pricing_budget_signal: GitHub Copilot · Plans & pricing · GitHub github.com public pricing pages :root pre, code {"locale":"en","featureFlags":["actions_cus Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: github.com is a public incumbent/source in category `public pricing pages`. ic_issue_marshal_yaml","copilot_ask_mode_dropdown","copilot_automation_session_author","copilot_chat_attach_multiple_images","copilot_chat_category_rate_limit_messages","copilot_chat_clear_model_selection_for_default_change","copilot_chat_c
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_004_e6_github_copilot_enterprise_billing_004
- cleaned_buyer_pain_signal: t Custom agents Hooks Access management MCP and cloud agent Risks and mitigations Copilot CLI About Copilot CLI Comparing CLI features Cancel and roll back About remote access Custom agents About CLI plugins Autonomous t
- cleaned_pricing_budget_signal: Plans Features Best practices Choose enterprise plan Achieve company goals Resources for approval Concepts Completions Code suggestions Code referencing Chat Agents Cloud agent Abo Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: or GitHub Copilot in organizations and enterprises - GitHub Docs docs.github.com public docs About billing for GitHub Copilot in organizations and enterprises - GitHub Docs Skip to main content GitHub Docs Version: Free, Pro, & Team Search
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_005_e6_langsmith_pricing_006
- cleaned_buyer_pain_signal: Seed sought agent observability, evaluation, pricing, production AI workflow buyer process; excerpt requires human review.
- cleaned_pricing_budget_signal: LangSmith Plans and Pricing www.langchain.com public pricing pages LangSmith Plans and Pricing html.w-mod-js:not(.w-mod-ix3) :is([text-paragraph-animation-start], [text-paragraph-animation]) {visibili Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: www.langchain.com is a public incumbent/source in category `public pricing pages`.
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_006_e6_crewai_pricing_007
- cleaned_buyer_pain_signal: Seed sought agentic workflow platform, pricing, enterprise support, implementation alternative; excerpt requires human review.
- cleaned_pricing_budget_signal: Pricing www.crewai.com public pricing pages Pricing Docume Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: www.crewai.com is a public incumbent/source in category `public pricing pages`.
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_007_e6_zapier_pricing_008
- cleaned_buyer_pain_signal: Seed sought automation pricing, AI orchestration, incumbent workflow platform, no-code substitute; excerpt requires human review.
- cleaned_pricing_budget_signal: Plans & Pricing | Zapier zapier.com public pricing pages Plans & Pricing | Zapier .zapier.com/Degular/DegularDisplay-Medium.woff2') for Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: zapier.com is a public incumbent/source in category `public pricing pages`.
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_008_e6_humanloop_pricing_009
- cleaned_buyer_pain_signal: Deployments Versioning and Tracking Feedback & Corrections Evaluation Eval Reports I
- cleaned_pricing_budget_signal: Humanloop Pricing GitHub icon LinkedIn icon humanloop.com public pricing pages Humanloop Pricing Humanloop is joining Anthropic View the announcement Download SVG Copy SVG Download Kit Platf Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: humanloop.com is a public incumbent/source in category `public pricing pages`. VG Copy SVG Download Kit Platform Pricing Case Studies Blog Docs Sign in Book a demo Pricing How great teams build AI products Get the enterprise platform to develop, evaluate, and ship trustworthy LLM powered apps.
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_009_e6_incident_io_pricing_011
- cleaned_buyer_pain_signal: Pricing | incident.io incident.io public pricing pages Pricing | incident.io {"@context":"https://schema.org","@type":"Organization","name":"incident.io","url":"https://incident.io","logo":"
- cleaned_pricing_budget_signal: Pricing | incident.io incident.io public pricing pages Pricing | incident.io {"@context":"https://schema.org","@type":"Organization","name":"incident.io","url":"https://incident.io Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: incident.io is a public incumbent/source in category `public pricing pages`. sets Download .PNG logos Download .SVG logos Download Brand Guidelines Visit brand center Products Solutions Resources Customers Pricing Careers Open main menu Products Solutions Resources Customers Pricing Careers Get a demo Login incident
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_010_e6_rootly_pricing_012
- cleaned_buyer_pain_signal: "en", "description": "Pricing plans for Rootly's AI-powered incident response and on-call management platform. Essentials plan at $20/user/month for startups and Enterprise plans for large organizations.", "about": { "@type": "SoftwareAppli
- cleaned_pricing_budget_signal: Rootly | Pricing rootly.com public pricing pages Rootly | Pricing Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: rootly.com is a public incumbent/source in category `public pricing pages`. ootly's AI-powered incident response and on-call management platform. Essentials plan at $20/user/month for startups and Enterprise plans for large organizations.", "about": { "@type": "SoftwareApplication", "name": "Rootly", "applicationCa
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_011_e6_github_sponsors_013
- cleaned_buyer_pain_signal: lling_ui_visibility","actions_image_version_event","actions_workflow_language_service_allow_concurrency_queue","agent_conflict_resolution","alternate_user_config_repo","arianotify_comprehensive_migration","billing_discount_threshold_notific
- cleaned_pricing_budget_signal: locale":"en","featureFlags":["actions_custom_images_storage_billing_ui_visibility","actions_image_version_event","actions_workflow_language_service_allow_concurrency_queue","agent_conflict_resolution","alternate_user_config_repo","arianotif Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: ic_issue_marshal_yaml","copilot_ask_mode_dropdown","copilot_automation_session_author","copilot_chat_attach_multiple_images","copilot_chat_category_rate_limit_messages","copilot_chat_clear_model_selection_for_default_change","copilot_chat_c
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_012_e6_aws_genai_partners_015
- cleaned_buyer_pain_signal: es AWS Partners | Generative AI | AWS {"noLoadEventRetriggers": true, "non
- cleaned_pricing_budget_signal: tners | Generative AI | AWS aws.amazon.com public ecosystem/marketplace pages AWS Partners | Generative AI | AWS {"pageLanguage":"en","supportedLanguages":["ar","cn","de","en","es","fr","id","it","jp","ko","pt","ru","th","tr","tw","vi"],"of
- cleaned_competitor_substitute_signal: aws.amazon.com is a public incumbent/source in category `public ecosystem/marketplace pages`.
- cleaned_buying_process_signal: tners | Generative AI | AWS aws.amazon.com public ecosystem/marketplace pages AWS Partners | Generative AI | AWS {"pageLanguage":"en","supportedLanguages":["ar","cn","de","en","es","fr","id","it","jp","ko","pt","ru","th","tr","tw","vi"],"of
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
### e6_source_seeded_public_page_read_source_013_e6_retool_pricing_017
- cleaned_buyer_pain_signal: eb apps, mobile apps, AI-powered apps, and custom logic and automations in Retool.
- cleaned_pricing_budget_signal: Retool | Pricing retool.com public pricing pages Retool | Pricing (function(a){let b=a.fetch;a.fetch=function(c,d){let e=c,f=d;try{let b=void 0!==a.Request&&c instanceof a.Request,g=new a.H Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- cleaned_competitor_substitute_signal: retool.com is a public incumbent/source in category `public pricing pages`. apps, and custom logic and automations in Retool.
- cleaned_buying_process_signal: Public pricing/billing/plan language provides a budget proxy; owner review still needed before commercial use.
- trust_gap_signal: Evidence supports a trust/category gap, not customer validation.
