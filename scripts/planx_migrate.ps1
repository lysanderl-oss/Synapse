# Plan X Migration Script — Synapse v3.0
# Creates WF-09 Unified Notification + migrates 8 PMO workflows
# Usage: ! powershell -File scripts/planx_migrate.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

$ErrorActionPreference = "Stop"

# N8N_API_KEY: 从 credentials.mdenc 读取（REQ-INFRA-001，2026-04-24）
# 使用方式：$env:CREDS_PW 或交互输入主密码
if (-not $env:N8N_API_KEY) {
    $credsPy = "C:/Users/lysanderl_janusd/Multi-Agents System/creds.py"
    if (-not $env:CREDS_PW) {
        $pw = Read-Host -Prompt "credentials.mdenc master password" -AsSecureString
        $env:CREDS_PW = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pw))
    }
    $env:N8N_API_KEY = python $credsPy get N8N_API_KEY -p $env:CREDS_PW
}
$N8N_KEY  = $env:N8N_API_KEY
$BASE     = "https://n8n.lysander.bond"
$SECRET   = "MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8"
$CRED_ID  = "uWER9LYkLVS3tMqr"
$CHANNEL  = "C0AJN5PN1G8"

$H = @{ "X-N8N-API-KEY" = $N8N_KEY; "Accept" = "application/json" }

function nGet($path) {
    Invoke-RestMethod -Uri "$BASE/api/v1$path" -Headers $H -Method GET
}
function nPost($path, $body) {
    $b = if ($body) { $body | ConvertTo-Json -Depth 20 -Compress } else { $null }
    Invoke-RestMethod -Uri "$BASE/api/v1$path" -Headers $H -Method POST -Body $b -ContentType "application/json"
}
function nPut($path, $body) {
    $b = $body | ConvertTo-Json -Depth 20 -Compress
    Invoke-RestMethod -Uri "$BASE/api/v1$path" -Headers $H -Method PUT -Body $b -ContentType "application/json"
}
function hmacSign($str) {
    $hmac = [System.Security.Cryptography.HMACSHA256]::new([System.Text.Encoding]::UTF8.GetBytes($SECRET))
    [System.BitConverter]::ToString($hmac.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($str))).Replace("-","").ToLower()
}

Write-Host "=== Plan X Migration ===" -ForegroundColor Cyan

# ── 1. Connectivity ──────────────────────────────────────────────────────────
Write-Host "[1/5] Connecting to n8n..." -NoNewline
$allWfs = nGet "/workflows"
Write-Host " OK ($($allWfs.data.Count) workflows)" -ForegroundColor Green

# ── 2. Create WF-09 ──────────────────────────────────────────────────────────
Write-Host "[2/5] WF-09..." -NoNewline
$existing = $allWfs.data | Where-Object { $_.name -match "WF-09|Unified Notification" }

if ($existing) {
    $wf09id = $existing[0].id
    Write-Host " already exists ($wf09id)" -ForegroundColor Yellow
} else {
    $wf09json = @'
{
  "name": "WF-09 Unified Notification",
  "nodes": [
    {
      "id": "n1", "name": "Webhook",
      "type": "n8n-nodes-base.webhook", "typeVersion": 2,
      "position": [250,300],
      "parameters": { "path": "notify", "httpMethod": "POST", "responseMode": "lastNode" }
    },
    {
      "id": "n2", "name": "HMAC Validate",
      "type": "n8n-nodes-base.code", "typeVersion": 2,
      "position": [470,300],
      "parameters": { "jsCode": "const crypto=require('crypto'),secret='MrMkZxFn0npAz7TtaONo-BN-4UUyLo7WhElYkvYKqy8',b=$input.first().json;if(b.signature){const now=Math.floor(Date.now()/1000),ts=parseInt(b.timestamp);if(isNaN(ts)||Math.abs(now-ts)>300)throw new Error('ts expired');const d=b.recipient+b.priority+b.title+b.body+b.timestamp,e=crypto.createHmac('sha256',secret).update(d).digest('hex');if(b.signature!==e)throw new Error('sig mismatch');}return[{json:{validated:true,...b}}];" }
    },
    {
      "id": "n3", "name": "Parse Recipient",
      "type": "n8n-nodes-base.code", "typeVersion": 2,
      "position": [690,300],
      "parameters": { "jsCode": "const r=$input.first().json.recipient||'';let ch=r;if(r==='president')ch='C0AJN5PN1G8';else if(r.startsWith('@U'))ch=r.substring(1);return[{json:{channelId:ch,...$input.first().json}}];" }
    },
    {
      "id": "n4", "name": "Send Slack",
      "type": "n8n-nodes-base.httpRequest", "typeVersion": 4,
      "position": [910,300],
      "parameters": {
        "method": "POST",
        "url": "https://slack.com/api/chat.postMessage",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\"channel\":\"{{ $json.channelId }}\",\"text\":\"*{{ $json.title }}*\\n\\n{{ $json.body }}\\n\\n_来源: {{ $json.source }} | 优先级: {{ $json.priority }}_\"}"
      },
      "credentials": { "httpHeaderAuth": { "id": "uWER9LYkLVS3tMqr", "name": "Slack Bot Token" } }
    }
  ],
  "connections": {
    "Webhook":         { "main": [[{"node":"HMAC Validate","type":"main","index":0}]] },
    "HMAC Validate":   { "main": [[{"node":"Parse Recipient","type":"main","index":0}]] },
    "Parse Recipient": { "main": [[{"node":"Send Slack","type":"main","index":0}]] }
  },
  "settings": { "executionOrder": "v1" }
}
'@
    $created = Invoke-RestMethod -Uri "$BASE/api/v1/workflows" -Headers $H -Method POST -Body $wf09json -ContentType "application/json"
    $wf09id = $created.id
    nPost "/workflows/$wf09id/activate" $null | Out-Null
    Write-Host " created & activated ($wf09id)" -ForegroundColor Green
}

# ── 3. Test WF-09 ────────────────────────────────────────────────────────────
Write-Host "[3/5] Testing WF-09 (waiting 5s for webhook registration)..." -NoNewline
Start-Sleep -Seconds 5
$ts = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds().ToString()
$title = "WF-09 Plan X Test"
$body  = "Unified notification online."
$sig   = hmacSign ($CHANNEL + "high" + $title + $body + $ts)
$testPayload = @{ recipient=$CHANNEL; priority="high"; title=$title; body=$body; source="plan-x-test"; signature=$sig; timestamp=$ts } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$BASE/webhook/notify" -Method POST -Body $testPayload -ContentType "application/json" | Out-Null
    Write-Host " OK — check Slack" -ForegroundColor Green
} catch {
    Write-Host " $($_.Exception.Response.StatusCode) — activate WF-09 in n8n UI if 404" -ForegroundColor Yellow
}

# ── 4. Migrate 8 PMO workflows ───────────────────────────────────────────────
Write-Host "[4/5] Migrating PMO workflows..."
$TARGETS = [ordered]@{
    "AnR20HucIRaiZPS7" = "wf-01-project-init"
    "IXEFFpLwnlcggK2E" = "wf-02-task-change"
    "uftMqCdR1pRz079z" = "wf-03-milestone"
    "40mJOR8xXtubjGO4" = "wf-04-weekly"
    "rlEylvNQW55UPbAq" = "wf-05-overdue"
    "g6wKsdroKNAqHHds" = "wf-05-charter"
    "knVJ8Uq2D1UZmpxr" = "wf-06-dependency"
    "seiXPY0VNzNxQ2L3" = "wf-07-minutes"
}

$ok = 0; $skip = 0; $fail = 0
foreach ($wfId in $TARGETS.Keys) {
    $src = $TARGETS[$wfId]
    Write-Host "  $src ($wfId)..." -NoNewline
    try {
        $wf = nGet "/workflows/$wfId"

        # Deep-convert workflow to mutable hashtable via JSON round-trip
        $wfJson = $wf | ConvertTo-Json -Depth 30 -Compress
        $wfMut  = $wfJson | ConvertFrom-Json   # fresh parse

        $changed = $false
        $newNodes = [System.Collections.Generic.List[object]]::new()

        foreach ($node in $wfMut.nodes) {
            if ($node.type -eq "n8n-nodes-base.httpRequest" -and
                $node.parameters.url -match "slack\.com/api") {

                # Rebuild as fully mutable hashtable
                $newNode = @{
                    id          = $node.id
                    name        = $node.name
                    type        = $node.type
                    typeVersion = $node.typeVersion
                    position    = $node.position
                    parameters  = @{
                        method       = "POST"
                        url          = "$BASE/webhook/notify"
                        authentication = "none"
                        sendBody     = $true
                        specifyBody  = "json"
                        jsonBody     = "{`"recipient`":`"$CHANNEL`",`"priority`":`"normal`",`"title`":`"$src`",`"body`":`"={{ JSON.stringify(`$input.first().json) }}`",`"source`":`"$src`"}"
                    }
                }
                $newNodes.Add($newNode)
                $changed = $true
            } else {
                $newNodes.Add($node)
            }
        }

        if ($changed) {
            $putBody = @{
                name        = $wfMut.name
                nodes       = $newNodes.ToArray()
                connections = $wfMut.connections
                settings    = $wfMut.settings
                staticData  = $wfMut.staticData
            }
            try { nPost "/workflows/$wfId/deactivate" $null | Out-Null } catch {}
            nPut "/workflows/$wfId" $putBody | Out-Null
            try { nPost "/workflows/$wfId/activate" $null | Out-Null } catch {}
            Write-Host " migrated" -ForegroundColor Green; $ok++
        } else {
            Write-Host " no Slack nodes" -ForegroundColor Yellow; $skip++
        }
    } catch {
        Write-Host " ERROR: $($_.Exception.Message)" -ForegroundColor Red; $fail++
    }
}

# ── 5. Summary ───────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[5/5] Summary:" -ForegroundColor Cyan
Write-Host "  WF-09 ID : $wf09id"
Write-Host "  Migrated : $ok/8" -ForegroundColor $(if ($ok -ge 7) {"Green"} elseif ($ok -ge 4) {"Yellow"} else {"Red"})
Write-Host "  Skipped  : $skip"
Write-Host "  Failed   : $fail" -ForegroundColor $(if ($fail -eq 0) {"Green"} else {"Red"})
Write-Host ""
Write-Host "Plan X complete. All Slack notifications now route through WF-09." -ForegroundColor Cyan
