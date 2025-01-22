# templates/_helpers.tpl
{{- define "lazy-lecture.labels" -}}
app.kubernetes.io/name: "{{ include "lazy-lecture.name" . }}"
app.kubernetes.io/instance: "{{ .Release.Name }}"
app.kubernetes.io/version: "{{ .Chart.AppVersion }}"
app.kubernetes.io/managed-by: "{{ .Release.Service }}"
{{- end }}

{{- define "lazy-lecture.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "lazy-lecture.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}

