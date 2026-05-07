#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::Mutex;

use tauri::Manager;
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::ShellExt;

struct BridgeSidecarState(Mutex<Option<CommandChild>>);

fn should_manage_sidecar_with_env(env_value: Option<&str>) -> bool {
    !cfg!(debug_assertions) || env_value == Some("1")
}

fn should_manage_sidecar() -> bool {
    should_manage_sidecar_with_env(std::env::var("KURONEKO_STUDIO_MANAGED_SIDECAR").ok().as_deref())
}

fn stop_sidecar(app: &tauri::AppHandle) {
    let child = {
        let state = app.state::<BridgeSidecarState>();
        let child = state.0.lock().unwrap().take();
        child
    };

    if let Some(child) = child {
        let _ = child.kill();
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(BridgeSidecarState(Mutex::new(None)))
        .setup(|app| {
            if should_manage_sidecar() {
                let sidecar = app.shell().sidecar("kuroneko-studio-bridge")?;
                let (_rx, child) = sidecar.spawn()?;

                let state = app.state::<BridgeSidecarState>();
                *state.0.lock().unwrap() = Some(child);
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            if matches!(
                event,
                tauri::WindowEvent::CloseRequested { .. } | tauri::WindowEvent::Destroyed
            ) {
                let app_handle = window.app_handle();
                stop_sidecar(&app_handle);
            }
        })
        .build(tauri::generate_context!())
        .expect("error while building KuroNeko Studio")
        .run(|app, event| {
            if let tauri::RunEvent::Exit = event {
                stop_sidecar(app);
            }
        });
}

#[cfg(test)]
mod tests {
    use super::should_manage_sidecar_with_env;

    #[test]
    fn enables_managed_sidecar_when_flag_is_set() {
        assert!(should_manage_sidecar_with_env(Some("1")));
    }

    #[test]
    fn keeps_managed_sidecar_disabled_in_debug_without_flag() {
        if cfg!(debug_assertions) {
            assert!(!should_manage_sidecar_with_env(None));
            assert!(!should_manage_sidecar_with_env(Some("0")));
        }
    }
}
