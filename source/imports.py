import sys, os, re, time, random, json, shutil, traceback, glob, html, copy
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from msvcrt import getch
from pathlib import Path
from xml.sax import saxutils

import requests, pyperclip
from bs4 import BeautifulSoup as bs
