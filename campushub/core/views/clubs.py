from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Club, ClubManager, Institution

# Legacy club settings views removed in favor of consolidated dashboard and club profile.
