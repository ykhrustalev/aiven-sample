from webcheck.monitoring import ResultsWorker


def test_execute(
    mocker,
    consumer,
    repo_results,
    result1, result2, result3,
):
    worker = ResultsWorker(consumer, repo_results)

    consumer.receive.return_value = [result1, result2, result3]
    repo_results.create.check.side_effect = (
        result1, Exception('foo'), result3
    )

    worker.execute()

    consumer.receive.assert_called_once_with()

    assert 3 == repo_results.create.call_count
    repo_results.create.assert_has_calls([
        mocker.call(result1),
        mocker.call(result2),
        mocker.call(result3),
    ])
