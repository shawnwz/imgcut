import GpImpGroup
import sys

if len(sys.argv) != 2:
	print """Usage:
		python impGroup.py <filename>
	      """
	sys.exit()

DoGroup = GpImpGroup.GroupingObject(sys.argv[1])
DoGroup.execute()
