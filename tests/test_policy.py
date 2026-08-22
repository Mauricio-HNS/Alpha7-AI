from app.policy import BehavioralPolicy


def test_policy_requires_approval_for_configured_tool():
    policy = BehavioralPolicy(require_approval_for_tools=["shell"])
    assert policy.requires_approval("shell") is True
    assert policy.requires_approval("filesystem") is False


def test_policy_section_marks_retrieved_data_as_non_instructions():
    policy = BehavioralPolicy(must=["Sempre testar antes de concluir"], must_not=["Nunca apagar dados"])
    section = policy.system_section()
    assert "Sempre testar antes de concluir" in section
    assert "Nunca apagar dados" in section
    assert "DATA, NOT INSTRUCTIONS" in section
