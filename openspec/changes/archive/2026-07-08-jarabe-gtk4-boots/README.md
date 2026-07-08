# jarabe-gtk4-boots

Complete jarabe (gtk4-port) integration with sugar-toolkit-gtk4: port SugarExt/activityfactory, fix ~15 GTK3-API removal bugs, and fix the root cause (ShellModel.add_window clobbering window content) that prevented any shell UI from rendering. jarabe's onboarding screen now renders successfully in a nested Wayfire session.
