import queue


def print_container_log(log_queue, window, output_key):
    queue_empty = False
    while not queue_empty:
        try:
            output = log_queue.get(block=False)
            log_queue.task_done()
            window[output_key].print(output, end='')
        except queue.Empty:
            queue_empty = True
            pass
