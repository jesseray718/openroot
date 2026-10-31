import sys

def log_failure(input_q, wrong_a, correct_a):
    with open("data/failure_log.jsonl", "a") as f:
        f.write(f'{{"input": "{input_q}", "wrong": "{wrong_a}", "correct": "{correct_a}"}}\n')
    print("[banked] Failure captured in FAILURE_POD. System will not repeat this mistake.")

if __name__ == "__main__":
    if len(sys.argv) > 3:
        log_failure(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: feedback_loop.py 'query' 'wrong_ans' 'correct_ans'")
