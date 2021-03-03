import React from "react";
import { Link } from "react-router-dom";

import HorizontalScroller from "../../../components/HorizontalScroller";
import IconButton from "../../../components/IconButton";
import { CalendarIcon, MoreIcon } from "../../../components/Icons";
import TextBody from "../../../components/TextBody";
import { Community } from "../../../pb/communities_pb";
import { routeToCommunityEvents } from "../../../routes";
import { EVENTS_EMPTY_STATE, SEE_MORE_EVENTS_LABEL } from "../../constants";
import { useCommunityPageStyles } from "./CommunityPage";
import EventCard from "./EventCard";
import SectionTitle from "./SectionTitle";

export default function PlacesSection({
  community,
}: {
  community: Community.AsObject;
}) {
  const classes = useCommunityPageStyles();

  return (
    <>
      <SectionTitle icon={<CalendarIcon />}>Events</SectionTitle>
      {
        //{eventsError && <Alert severity="error">{eventsError.message}</Alert>}
        //{isEventsLoading && <CircularProgress />}
      }
      <HorizontalScroller className={classes.cardContainer}>
        {[0, 1, 2, 3].length === 0 ? (
          <TextBody>{EVENTS_EMPTY_STATE}</TextBody>
        ) : (
          [0, 1, 2, 3, 4, 5, 6].map((i) => (
            <EventCard
              key={`eventcard-${i}`}
              event={{
                title: "Placeholder event",
                creatorName: "Bot",
                location: "Amsterdam",
                startTime: { seconds: Date.now() / 1000, nanos: 0 },
              }}
              className={classes.placeEventCard}
            />
          ))
        )}
        {true && ( //eventsHasNextPage && (
          <div className={classes.loadMoreButton}>
            <Link
              to={routeToCommunityEvents(community.communityId, community.slug)}
            >
              <IconButton aria-label={SEE_MORE_EVENTS_LABEL}>
                <MoreIcon />
              </IconButton>
            </Link>
          </div>
        )}
      </HorizontalScroller>
    </>
  );
}
