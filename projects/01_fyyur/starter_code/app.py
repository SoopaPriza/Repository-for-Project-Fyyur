#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime as dt
from models import *

#db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  dictionary={}
  venues=Venue.query.all()
  for venue in venues:
    location=(venue.city, venue.state)
    if location in dictionary:
      dictionary[location]["venues"].append({
                                      "id": venue.id,
                                      "name": venue.name})
    else:
      dictionary[location]={"city": venue.city,
                             "state": venue.state,
                             "venues": [{
                               "id": venue.id,
                               "name": venue.name}]}
  # return render_template('pages/venues.html', areas=data)
  return render_template('pages/venues.html', areas=dictionary.values())

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  response={}
  result = Venue.query.filter(Venue.name.ilike('%' + request.form.get('search_term') + '%')).all()
  response["count"]=len(result)
  response["data"]=result
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
# return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  result = Venue.query.get(venue_id)
  result.genres = result.genres.strip('][').replace("'", "").split(', ')
  result.upcoming_shows=Show.query.filter_by(venue_id=venue_id).filter(Show.start_time > dt.now()).all()
  result.upcoming_shows_count=len(result.upcoming_shows)
  result.past_shows=Show.query.filter_by(venue_id=venue_id).filter(Show.start_time < dt.now()).all()
  result.past_shows_count=len(result.past_shows)
  for show in result.upcoming_shows:
    show.start_time=str(show.start_time)
    artist=Artist.query.get(show.artist_id)
    show.artist_name=artist.name
    show.artist_image_link=artist.image_link
  for show in result.past_shows:
    show.start_time=str(show.start_time)
    artist=Artist.query.get(show.artist_id)
    show.artist_name=artist.name
    show.artist_image_link=artist.image_link
  return render_template('pages/show_venue.html', venue=result)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = VenueForm(request.form)
    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=str(form.genres.data),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      looking_for_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue: {0} created successfully'.format(venue.name))
  except Exception as err:
    flash('An error occurred creating the Venue')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')
  # try:
  #   name = request.form['name']
  #   city = request.form['city']
  #   state = request.form['state']
  #   address = request.form['address']
  #   phone = request.form['phone']
  #   genres = str(request.form.getlist('genres'))
  #   facebook_link = request.form['facebook_link']
  #   image_link = request.form['image_link']
  #   website_link = request.form['website_link']
  #   looking_for_talent = True if 'seeking_talent' in request.form else False
  #   seeking_description = request.form['seeking_description']
  #   venue = Venue(name = name,
  #                 city = city, 
  #                 state = state, 
  #                 address = address, 
  #                 phone = phone, 
  #                 genres = genres, 
  #                 facebook_link = facebook_link, 
  #                 image_link = image_link, 
  #                 website_link = website_link, 
  #                 looking_for_talent = looking_for_talent, 
  #                 seeking_description = seeking_description)
  #   db.session.add(venue)
  #   db.session.commit()
  #   data = Venue.query.get(venue.id)
  #   flash('Venue ' + data.name + ' was successfully listed!')
  # except:
  #   db.session.rollback()
  #   flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # finally:
  #   db.session.close()
  # return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue=Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except Exception as error:
    db.session.rollback()
    flash("Oooooops, something went wrong... :/")
  finally:
    db.session.close()
  return render_template('pages/home.html')
  #return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response={}
  result = Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term') + '%')).all()
  response["count"]=len(result)
  response["data"]=result
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  result = Artist.query.get(artist_id)
  result.genres = result.genres.strip('][').replace("'", "").split(', ')
  result.upcoming_shows=Show.query.filter_by(artist_id=artist_id).filter(Show.start_time > dt.now()).all()
  result.upcoming_shows_count=len(result.upcoming_shows)
  result.past_shows=Show.query.filter_by(artist_id=artist_id).filter(Show.start_time < dt.now()).all()
  result.past_shows_count=len(result.past_shows)
  for show in result.upcoming_shows:
    show.start_time=str(show.start_time)
    venue=Venue.query.get(show.venue_id)
    show.venue_name=venue.name
    show.venue_image_link=venue.image_link
  for show in result.past_shows:
    show.start_time=str(show.start_time)
    venue=Venue.query.get(show.venue_id)
    show.venue_name=venue.name
    show.venue_image_link=venue.image_link
  return render_template('pages/show_artist.html', artist=result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  result = Artist.query.get(artist_id)
  result.genres = result.genres.strip('][').replace("'", "").split(', ')
  form = ArtistForm(state=result.state, genres=result.genres, seeking_venue=result.looking_for_venues)
  return render_template('forms/edit_artist.html', form=form, artist=result)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = str(request.form.getlist('genres'))
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website_link']
  looking_for_venues = True if 'seeking_venue' in request.form else False
  seeking_description = request.form['seeking_description']
  artist = Artist.query.get(artist_id)
  artist.name = name
  artist.city = city
  artist.state = state
  artist.phone = phone
  artist.genres = genres
  artist.facebook_link = facebook_link
  artist.image_link = image_link
  artist.website = website
  artist.looking_for_venues = looking_for_venues
  artist.seeking_description = seeking_description
  db.session.add(artist)
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  result = Venue.query.get(venue_id)
  result.genres = result.genres.strip('][').replace("'", "").split(', ')
  form = VenueForm(state=result.state, genres=result.genres, seeking_talent=result.looking_for_talent)
  return render_template('forms/edit_venue.html', form=form, venue=result)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = str(request.form.getlist('genres'))
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website_link']
  looking_for_talent = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']
  venue = Venue.query.get(venue_id)
  venue.name = name
  venue.city = city
  venue.state = state
  venue.address = address
  venue.phone = phone
  venue.genres = genres
  venue.facebook_link = facebook_link
  venue.image_link = image_link
  venue.website = website
  venue.looking_for_talent = looking_for_talent
  venue.seeking_description = seeking_description
  db.session.add(venue)
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form = ArtistForm(request.form)
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=str(form.genres.data),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website_link.data,
      looking_for_venues=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist: {0} created successfully'.format(artist.name))
  except Exception as err:
    flash('An error occurred creating the Artist')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')
  # try:
  #   name = request.form['name']
  #   city = request.form['city']
  #   state = request.form['state']
  #   phone = request.form['phone']
  #   genres = str(request.form.getlist('genres'))
  #   facebook_link = request.form['facebook_link']
  #   image_link = request.form['image_link']
  #   website = request.form['website_link']
  #   looking_for_venues = True if 'seeking_venue' in request.form else False
  #   seeking_description = request.form['seeking_description']
  #   artist = Artist(name = name,
  #                 city = city, 
  #                 state = state,
  #                 phone = phone, 
  #                 genres = genres, 
  #                 facebook_link = facebook_link, 
  #                 image_link = image_link, 
  #                 website = website, 
  #                 looking_for_venues = looking_for_venues, 
  #                 seeking_description = seeking_description)
  #   db.session.add(artist)
  #   db.session.commit()
  #   data = Venue.query.get(artist.id)
  #   flash('Artist ' + data.name + ' was successfully listed!')
  # except:
  #   db.session.rollback()
  #   flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # finally:
  #   db.session.close()
  # return render_template('pages/home.html')

  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  shows=Show.query.join(Artist).all()
  for show in shows:
    show.start_time=str(show.start_time)
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = ShowForm(request.form)
    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )
    # artist_id = request.form['artist_id']
    # venue_id = request.form['venue_id']
    # start_time = request.form['start_time']
    # show = Show(artist_id = artist_id,
    #             venue_id = venue_id,
    #             start_time = start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. This show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
