"""
Unit and integration tests for Security Analyst Agent (Requirement 3).
Tests both built-in presets and dynamic behavioral evaluation of custom arbitrary logs.
"""

import pytest
import pytest_asyncio
from backend.agents.security_agent import security_agent, SecurityRuleEngine
from backend.models.schemas import SecurityAnalysisRequest, SeverityLevel


@pytest.mark.asyncio
async def test_security_analysis_ssh_brute_force():
    logs = (
        "Mar 14 03:12:01 edge-gateway-01 sshd[14201]: Failed password for root from 198.51.100.42 port 48210 ssh2\n"
        "Mar 14 03:12:03 edge-gateway-01 sshd[14204]: Failed password for admin from 198.51.100.42 port 48214 ssh2\n"
        "Mar 14 03:12:06 edge-gateway-01 sshd[14209]: Failed password for deploy from 198.51.100.42 port 48220 ssh2\n"
        "Mar 14 03:13:05 edge-gateway-01 sshd[14325]: Accepted password for deploy from 198.51.100.42 port 48330 ssh2\n"
        "Mar 14 03:13:12 edge-gateway-01 sudo[14339]: deploy : TTY=pts/2 ; PWD=/home/deploy ; USER=root ; COMMAND=/bin/bash"
    )

    req = SecurityAnalysisRequest(raw_logs=logs, log_type="auth")
    res = await security_agent.analyze_logs(req)

    assert res.analysis_id.startswith("sec_")
    assert res.severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL)
    assert res.confidence >= 0.85
    assert len(res.mitigations) > 0
    assert any("198.51.100.42" in ind for ind in res.indicators) or len(res.indicators) > 0


@pytest.mark.asyncio
async def test_security_analysis_custom_arbitrary_logs():
    """Verify that arbitrary custom logs from novel IPs are dynamically parsed and triaged."""
    custom_logs = (
        "2026-03-15T04:11:00Z web-lb01 nginx: 203.0.113.199 - - GET /api/v1/users?id=1 UNION SELECT table_name,column_name FROM information_schema.columns HTTP/1.1 200 4120 sqlmap/1.8\n"
        "2026-03-15T04:11:05Z web-lb01 nginx: 203.0.113.199 - - GET /api/v1/admin/exec?cmd=powershell%20-enc%20SQBFAFgA HTTP/1.1 500 124 sqlmap/1.8\n"
        "2026-03-15T04:11:10Z web-lb01 nginx: 203.0.113.199 - - GET /api/v1/auth/session HTTP/1.1 200 89"
    )

    req = SecurityAnalysisRequest(raw_logs=custom_logs, log_type="web")
    res = await security_agent.analyze_logs(req)

    assert res.severity == SeverityLevel.CRITICAL
    assert "sql" in res.threat.lower() or "injection" in res.threat.lower() or "sql" in res.attack_type.lower()
    assert any("203.0.113.199" in ind for ind in res.indicators)
    assert len(res.mitigations) >= 1
    assert res.mitigations[0].priority in ("IMMEDIATE", "INVESTIGATION", "LONG_TERM", "DETECTION_RULE")


def test_security_rule_engine_standalone():
    """Verify standalone dynamic rule engine parsing across different attack categories."""
    recon_logs = (
        "Mar 15 01:00:00 fw kernel: [IPTABLES-DROP] SRC=198.51.100.77 DST=10.0.0.1 PROTO=TCP SPT=40001 DPT=22 SYN\n"
        "Mar 15 01:00:01 fw kernel: [IPTABLES-DROP] SRC=198.51.100.77 DST=10.0.0.1 PROTO=TCP SPT=40002 DPT=80 SYN\n"
        "Mar 15 01:00:02 fw kernel: [IPTABLES-DROP] SRC=198.51.100.77 DST=10.0.0.1 PROTO=TCP SPT=40003 DPT=443 SYN\n"
        "Mar 15 01:00:03 fw kernel: [IPTABLES-DROP] SRC=198.51.100.77 DST=10.0.0.1 PROTO=TCP SPT=40004 DPT=3389 SYN\n"
        "Mar 15 01:00:04 fw kernel: [IPTABLES-DROP] SRC=198.51.100.77 DST=10.0.0.1 PROTO=TCP SPT=40005 DPT=8080 SYN"
    )
    eval_res = SecurityRuleEngine.analyze_stream(recon_logs, "firewall")
    assert eval_res["severity"] in ("MEDIUM", "HIGH")
    assert "port scan" in eval_res["threat"].lower() or "reconnaissance" in eval_res["threat"].lower()
    assert "198.51.100.77" in eval_res["indicators"]


def test_security_presets_available():
    presets = security_agent.get_presets()
    assert len(presets) >= 7
    preset_ids = [p.id for p in presets]
    assert "ssh-brute-force" in preset_ids
    assert "sqli-attack" in preset_ids
    assert "ransomware-c2" in preset_ids
