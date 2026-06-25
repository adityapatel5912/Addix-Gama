from gama.evaluators import security, db_stress

def scan(codebase_path):
    all_errors = []

    # Run security evaluator
    security_errors = security.evaluate(codebase_path)
    all_errors.extend(security_errors)

    # Run db_stress evaluator
    db_errors = db_stress.evaluate(codebase_path)
    all_errors.extend(db_errors)

    return all_errors
