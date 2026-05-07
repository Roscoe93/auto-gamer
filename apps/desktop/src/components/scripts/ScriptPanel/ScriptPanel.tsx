import React, { useEffect, useState } from "react";
import { BridgeClient, ScriptManifest, Profile, ConnectionState } from "../../../services/bridge-client";
import { Select } from "../../ui/Select";
import { Button } from "../../ui/Button";
import { DynamicForm } from "../../forms/DynamicForm";
import "./ScriptPanel.css";

export interface ScriptPanelProps {
  client: BridgeClient;
  connectionState: ConnectionState;
}

export const ScriptPanel: React.FC<ScriptPanelProps> = ({ client, connectionState }) => {
  const [scripts, setScripts] = useState<ScriptManifest[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]);

  const [selectedScriptId, setSelectedScriptId] = useState<string>("");
  const [selectedProfileId, setSelectedProfileId] = useState<string>("");
  const [formValues, setFormValues] = useState<Record<string, any>>({});
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const unsubscribe = client.subscribe((event) => {
      if (event.type === "scripts/listed") {
        setScripts(event.payload);
        if (event.payload.length > 0 && !selectedScriptId) {
          setSelectedScriptId(event.payload[0].id);
        }
      }
      if (event.type === "profiles/listed") {
        setProfiles(event.payload);
      }
      if (event.type === "profiles/saved") {
        client.listProfiles();
        setSelectedProfileId(event.payload.id);
        setIsSaving(false);
      }
      if (event.type === "profiles/deleted") {
        client.listProfiles();
        setSelectedProfileId("");
      }
    });

    if (connectionState === "connected") {
      client.listScripts();
      client.listProfiles();
    }

    return () => {
      unsubscribe();
    };
  }, [client, connectionState]);

  // When script changes, filter profiles and reset form
  useEffect(() => {
    if (!selectedScriptId) return;

    // Find matching profiles
    const scriptProfiles = profiles.filter(p => p.scriptId === selectedScriptId);

    if (selectedProfileId) {
      const currentProfile = scriptProfiles.find(p => p.id === selectedProfileId);
      if (currentProfile) {
        setFormValues(currentProfile.parameters);
        return;
      }
    }

    // Reset to default schema values
    const script = scripts.find(s => s.id === selectedScriptId);
    if (script && script.schema && script.schema.properties) {
      const defaults: Record<string, any> = {};
      Object.entries(script.schema.properties).forEach(([k, v]: [string, any]) => {
        if (v.default !== undefined) {
          defaults[k] = v.default;
        }
      });
      setFormValues(defaults);
    } else {
      setFormValues({});
    }
    setSelectedProfileId("");
  }, [selectedScriptId, profiles, scripts]);

  // When profile changes manually
  const handleProfileChange = (profileId: string) => {
    setSelectedProfileId(profileId);
    if (profileId) {
      const profile = profiles.find(p => p.id === profileId);
      if (profile) {
        setFormValues(profile.parameters);
      }
    }
  };

  const handleFormChange = (key: string, value: any) => {
    setFormValues(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveProfile = () => {
    if (!selectedScriptId) return;
    setIsSaving(true);
    client.saveProfile({
      id: selectedProfileId || undefined,
      scriptId: selectedScriptId,
      name: selectedProfileId ? profiles.find(p => p.id === selectedProfileId)?.name || "New Profile" : `配置 ${new Date().toLocaleTimeString()}`,
      parameters: formValues
    });
  };

  const handleDeleteProfile = () => {
    if (selectedProfileId) {
      client.deleteProfile(selectedProfileId);
    }
  };

  const script = scripts.find(s => s.id === selectedScriptId);
  const scriptProfiles = profiles.filter(p => p.scriptId === selectedScriptId);

  return (
    <div className="script-panel">
      <div className="script-panel-header">
        <div className="selector-group">
          <label>脚本</label>
          <Select
            value={selectedScriptId}
            onChange={(e) => setSelectedScriptId(e.target.value)}
            options={scripts.map(s => ({ value: s.id, label: s.name }))}
          />
        </div>
        <div className="selector-group">
          <label>配置</label>
          <Select
            value={selectedProfileId}
            onChange={(e) => handleProfileChange(e.target.value)}
            options={[
              { value: "", label: "默认配置 (未保存)" },
              ...scriptProfiles.map(p => ({ value: p.id, label: p.name }))
            ]}
          />
        </div>
      </div>

      {script && (
        <div className="script-panel-body">
          <div className="script-info">
            <h3>{script.name} <span className="version">v{script.version}</span></h3>
            <p>{script.description}</p>
            <span className="author">by {script.author}</span>
          </div>

          <div className="form-container">
            <DynamicForm
              schema={script.schema}
              values={formValues}
              onChange={handleFormChange}
            />
          </div>

          <div className="script-panel-actions">
            <Button
              variant="primary"
              onClick={handleSaveProfile}
              disabled={isSaving || !selectedScriptId}
            >
              {selectedProfileId ? "保存更新" : "另存为新配置"}
            </Button>
            {selectedProfileId && (
              <Button variant="stop" onClick={handleDeleteProfile}>
                删除配置
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
