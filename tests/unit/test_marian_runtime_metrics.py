from app.services import marian as marian_module


def setup_function():
    marian_module.reset_marian_runtime_metrics()


def teardown_function():
    marian_module.reset_marian_runtime_metrics()


def test_generation_failure_rate_is_computed_from_attempts_and_failures():
    marian_module.record_marian_generation_attempt()
    marian_module.record_marian_generation_attempt()
    marian_module.record_marian_generation_failure("mock failure")

    runtime = marian_module.get_marian_runtime_info()

    assert runtime["generation_attempts"] == 2
    assert runtime["generation_failures"] == 1
    assert runtime["generation_failure_rate"] == 0.5
    assert runtime["last_generation_error"] == "mock failure"


def test_generation_failure_rate_is_zero_when_no_attempts():
    runtime = marian_module.get_marian_runtime_info()

    assert runtime["generation_attempts"] == 0
    assert runtime["generation_failures"] == 0
    assert runtime["generation_failure_rate"] == 0.0
