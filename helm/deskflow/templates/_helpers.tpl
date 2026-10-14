{{- define "deskflow.labels" -}}
app.kubernetes.io/part-of: deskflow
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "deskflow.backendName" -}}{{ .Release.Name }}-backend{{- end -}}
{{- define "deskflow.frontendName" -}}{{ .Release.Name }}-frontend{{- end -}}
{{- define "deskflow.postgresName" -}}{{ .Release.Name }}-postgres{{- end -}}
