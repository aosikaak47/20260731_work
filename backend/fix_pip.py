import sys
import types

overlapped_stub = types.ModuleType('_overlapped')
overlapped_stub.Error = OSError
sys.modules['_overlapped'] = overlapped_stub

from pip._internal.cli.main import main
sys.exit(main())