import Alert from "components/Alert";
import Button from "components/Button";
import CircularProgress from "components/CircularProgress";
import EditLocationMap, {
  ApproximateLocation,
} from "components/EditLocationMap";
import TextField from "components/TextField";
import { pageURL } from "features/communities/redirect";
import ProfileMarkdownInput from "features/profile/ProfileMarkdownInput";
import { Error as GrpcError } from "grpc-web";
import { Page } from "pb/pages_pb";
import React from "react";
import { Controller, useForm } from "react-hook-form";
import { useMutation } from "react-query";
import { useHistory } from "react-router-dom";
import { service } from "service";

type NewPlaceInputs = {
  title: string;
  content: string;
  address: string;
  lat: number;
  lng: number;
};

export default function NewPlaceForm() {
  const {
    control,
    register,
    handleSubmit,
    setValue,
    errors,
  } = useForm<NewPlaceInputs>({
    mode: "onBlur",
    shouldUnregister: false,
  });

  const history = useHistory();

  const {
    mutate: createPlace,
    isLoading: isCreateLoading,
    error: createError,
  } = useMutation<Page.AsObject, GrpcError, NewPlaceInputs>(
    ({ title, content, address, lat, lng }: NewPlaceInputs) =>
      service.pages.createPlace(title, content, address, lat, lng),
    {
      onSuccess: (page) => {
        history.push(pageURL(page));
      },
    }
  );

  const onSubmit = handleSubmit((data: NewPlaceInputs) => createPlace(data));

  return (
    <>
      {createError && <Alert severity="error">{createError?.message}</Alert>}
      {isCreateLoading ? (
        <CircularProgress />
      ) : (
        <form onSubmit={onSubmit}>
          <TextField
            id="new-place-title"
            name="title"
            label="Place Title"
            inputRef={register({
              required: "Enter a page title",
            })}
            helperText={errors?.title?.message}
          />
          <ProfileMarkdownInput
            id="content"
            label="Place content"
            control={control}
            name="content"
          />

          <Controller
            name="address"
            control={control}
            render={() => (
              <EditLocationMap
                exact
                updateLocation={(location: ApproximateLocation) => {
                  setValue("address", location.address);
                  setValue("lat", location.lat);
                  setValue("lng", location.lng);
                }}
              />
            )}
          />

          <Button onClick={onSubmit} loading={isCreateLoading}>
            Create page
          </Button>
        </form>
      )}
    </>
  );
}
