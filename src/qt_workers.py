from aqt import QThread, pyqtSignal # , QObject, 
# import datetime

# from pocketbase_api import UpdateLBError
# import anki_stats
# from dev import info, error, log, popup


class TokenRefresher(QThread):
    success = pyqtSignal(bool)
    
    def __init__(self, pb):
        super().__init__()
        self.pb = pb

    def run(self):
        s = self.pb.refresh_user_token()
        self.success.emit(s)


# class LBSyncer(QObject):
#     finished = pyqtSignal()

#     def __init__(self, pb):
#         super().__init__()
#         self.pb = pb

#     def run(self):
#         log('LB syncer started')
        
#         r = anki_stats.get_review_count()
                
#         try:
#             self.pb.user.set_reviews(datetime.datetime.utcnow(), r)
            
#             log(f"Syncing review count to NAL: {r}")
#         except AttributeError:
#             info("User not logged in and tried to sync")
#         except UpdateLBError:
#             popup("Couldn't update leaderboard. Try logging out and back in.")
#         except Exception as e:
#             info(f"Error syncing review count to NAL. See log for details")
#             error()
            
#         self.finished.emit()
