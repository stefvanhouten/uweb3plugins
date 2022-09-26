import configparser

import uweb3


class RestrictedDebuggingMixin(uweb3.DebuggingPageMaker):
    """This debugging pagemaker only shows debugging info to those on the white-list"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_development = self.config.config.getboolean("general", "development")

    def _should_show_exception_page(self):
        """Determine whether we should show the exception page to the user or not.

        If the application is run in development mode always show the page.
        If the application is run in production mode only show the page if one
            of the following conditions are met:
                - The users IP address is in the white-list
                - The user is using a forawarded IP address
                    and the forwarded IP address is in the white-list
                    and the application allows forwarded IP addresses
        """
        if self.is_development:
            return True

        if (
            "debugging" not in self.options
            or "whitelist" not in self.options["debugging"]
        ):
            return False

        # Comma seperated list of IP addresses
        whitelist = self.options["debugging"]["whitelist"]
        if not whitelist:
            return False

        # Make sure no empty strings are in the list.
        whitelisted_addresses = list(filter(None, whitelist.split(",")))
        remote_address = self.req.env["REMOTE_ADDR"]

        if remote_address in whitelisted_addresses:
            return True

        # Attempt to parse the value to a boolean, default to false.
        try:
            useforwardedip = self.config.config.getboolean(
                "debugging", "useforwardedip"
            )
        except ValueError:
            self.logger.warning("Invalid useforwardedip setting found, assuming False")
            return False
        except configparser.NoOptionError:
            # Option was not present, so user is not authorized to see the page.
            return False

        try:
            real_address = self.req.env["HTTP_X_FORWARDED_FOR"]
        except KeyError:
            return False

        if useforwardedip and real_address in whitelisted_addresses:
            return True

        return False

    def InternalServerError(self, exc_type, exc_value, traceback):
        self.logger.exception(
            "Internal server error occured: ", exc_info=(exc_type, exc_value, traceback)
        )
        if self._should_show_exception_page():
            return super().InternalServerError(exc_type, exc_value, traceback)
        return self.Error("A server error occurred.", httpcode=500, log_error=False)  # type: ignore # noqa: E501
