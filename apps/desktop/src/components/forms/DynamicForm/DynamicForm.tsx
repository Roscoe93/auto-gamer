import React from "react";
import { Input } from "../../ui/Input";
import { Switch } from "../../ui/Switch";
import { Select } from "../../ui/Select";
import "./DynamicForm.css";

export interface DynamicFormProps {
  schema: Record<string, any>;
  values: Record<string, any>;
  onChange: (key: string, value: any) => void;
}

export const DynamicForm: React.FC<DynamicFormProps> = ({ schema, values, onChange }) => {
  if (!schema || !schema.properties) {
    return <p className="dynamic-form-empty">该脚本无需配置参数</p>;
  }

  const properties = schema.properties;

  return (
    <div className="dynamic-form">
      {Object.entries(properties).map(([key, prop]: [string, any]) => {
        const value = values[key] ?? prop.default;

        return (
          <div key={key} className="form-item">
            <div className="form-item-header">
              <label>{prop.title || key}</label>
              {prop.description && <span className="form-item-desc">{prop.description}</span>}
            </div>
            <div className="form-item-control">
              {prop.type === "boolean" && (
                <Switch checked={Boolean(value)} onChange={(val) => onChange(key, val)} />
              )}
              {prop.type === "string" && !prop.enum && (
                <Input value={String(value || "")} onChange={(val) => onChange(key, val)} />
              )}
              {prop.type === "integer" || prop.type === "number" ? (
                <Input
                  type="number"
                  value={String(value || "")}
                  onChange={(val) => onChange(key, Number(val))}
                  min={prop.minimum}
                  max={prop.maximum}
                />
              ) : null}
              {prop.enum && (
                <Select
                  value={String(value)}
                  onChange={(val) => onChange(key, val)}
                  options={prop.enum.map((e: string, idx: number) => ({
                    value: e,
                    label: prop.enumNames ? prop.enumNames[idx] : e
                  }))}
                />
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
