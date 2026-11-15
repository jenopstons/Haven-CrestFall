# One instance per HP point. The UI binding owns both state poses, so this
# works for loose files, atlas frames, and animated ranges alike. A state
# with no art hides the icon but keeps the other state's size for spacing.
lifePoses = UI_CONFIG['lives']['icon']
self.fullPose = _load_pose(lifePoses['full'])
self.emptyPose = _load_pose(lifePoses['empty'])
_apply_pose(self, self.fullPose or self.emptyPose)
self.visible = self.fullPose is not None
self.index = 0
self.filled = True
self.z = 100
