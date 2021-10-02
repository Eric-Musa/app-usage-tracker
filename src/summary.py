import psutil
from app_usage_tracker import (
    Application,
    categorize,
    OTHER,
)


class Summary:
    def __init__(self, exclude_other=True) -> None:
        self.applications = {}
        self.exclude_other = exclude_other

        for proc in psutil.process_iter():
            try:
                name = proc.name()
                if categorize(proc.exe()) == OTHER and exclude_other:
                    continue
                if name not in self.applications:
                    self.applications[name] = [Application.from_process(proc)]
                else:
                    self.applications[name][-1].add(proc)
            except psutil.AccessDenied as e:
                print(e)
        # for proc in psutil.process_iter():
        #     try:
        #         app = Application.from_process(proc)
        #         name = app.name
        #         if app.category == OTHER:
        #             continue
        #         if name not in self.applications:
        #             self.applications[name] = [app]
        #         else:
        #             if app == self.applications[name][-1]:
        #                 continue
        #             else:
        #                 self.applications[name].append(app)
        #     except psutil.AccessDenied as e:
        #         print(e)


if __name__ == "__main__":

    summary = Summary(exclude_other=False)
