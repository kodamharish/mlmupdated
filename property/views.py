# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


# ------------------ Property Category Views ------------------

class PropertyCategoryListCreateView(APIView):
    def get(self, request):
        try:
            categories = PropertyCategory.objects.all()
            serializer = PropertyCategorySerializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = PropertyCategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PropertyCategoryDetailView(APIView):
    def get_object(self, property_category_id):
        return get_object_or_404(PropertyCategory, property_category_id=property_category_id)

    def get(self, request, property_category_id):
        try:
            category = self.get_object(property_category_id)
            serializer = PropertyCategorySerializer(category)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, property_category_id):
        try:
            category = self.get_object(property_category_id)
            serializer = PropertyCategorySerializer(category, data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, property_category_id):
        try:
            category = self.get_object(property_category_id)
            category.delete()
            return Response({"message": "Property category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------ Property Type Views ------------------

class PropertyTypeListCreateView(APIView):
    def get(self, request):
        try:
            types = PropertyType.objects.all()
            serializer = PropertyTypeSerializer(types, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = PropertyTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PropertyTypeDetailView(APIView):
    def get_object(self, property_type_id):
        return get_object_or_404(PropertyType, property_type_id=property_type_id)

    def get(self, request, property_type_id):
        try:
            prop_type = self.get_object(property_type_id)
            serializer = PropertyTypeSerializer(prop_type)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, property_type_id):
        try:
            prop_type = self.get_object(property_type_id)
            serializer = PropertyTypeSerializer(prop_type, data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, property_type_id):
        try:
            prop_type = self.get_object(property_type_id)
            prop_type.delete()
            return Response({"message": "Property type deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------ Property Type by Category Name ------------------

class PropertyTypeByCategoryNameView(APIView):
    def get(self, request, category_name):
        try:
            category = PropertyCategory.objects.get(name__iexact=category_name)
            property_types = PropertyType.objects.filter(category=category)
            serializer = PropertyTypeSerializer(property_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PropertyCategory.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







# ------------------ Property Type by Category ID ------------------

class PropertyTypeByCategoryIDView(APIView):
    def get(self, request, category_id):
        try:
            category = PropertyCategory.objects.get(property_category_id=category_id)
            property_types = PropertyType.objects.filter(category=category)
            serializer = PropertyTypeSerializer(property_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PropertyCategory.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)










# ------------------ Property Views ------------------

# class PropertyListCreateView(APIView):
#     def get(self, request):
#         try:
#             properties = Property.objects.all()
#             serializer = PropertySerializer(properties, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         try:
#             serializer = PropertySerializer(data=request.data, context={'request': request})
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class PropertyListCreateView(APIView):
    
    def get(self, request):
        try:
            properties = Property.objects.all()
            response_data = []

            for prop in properties:
                prop_data = PropertySerializer(prop).data
                buyer_data = None

                # Check if the property has a booking or purchase
                try:
                    user_property = UserProperty.objects.get(property=prop)
                    user_info = UserSerializer(user_property.user).data
                    buyer_data = {
                        **user_info,
                        "booking_date": user_property.booking_date,
                        "purchase_date": user_property.purchase_date
                    }
                except UserProperty.DoesNotExist:
                    buyer_data = None

                prop_data["buyer_user"] = buyer_data
                response_data.append(prop_data)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = PropertySerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PropertyDetailView(APIView):
    def get_object(self, property_id):
        return get_object_or_404(Property, property_id=property_id)

    def get(self, request, property_id):
        try:
            property_instance = self.get_object(property_id)
            serializer = PropertySerializer(property_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, property_id):
        try:
            property_instance = self.get_object(property_id)
            serializer = PropertySerializer(property_instance, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, property_id):
        try:
            property_instance = self.get_object(property_id)
            property_instance.delete()
            return Response({"message": "Property deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# class LatestPropertiesAPIView(APIView):
#     def get(self, request):
#         # Calculate the date one month ago from today
#         one_month_ago = timezone.now() - timedelta(days=30)

#         # Fetch all properties created in the last month
#         new_properties = Property.objects.filter(created_at__gte=one_month_ago)

#         # Serialize the properties (use the appropriate serializer for your properties)
#         serializer = PropertySerializer(new_properties, many=True)

#         return Response(serializer.data, status=status.HTTP_200_OK)




class LatestPropertiesAPIView(APIView):
    def get(self, request, user_id=None):
        try:
            one_month_ago = timezone.now() - timedelta(days=30)

            # Filter by user_id if provided
            if user_id:
                properties = Property.objects.filter(user_id=user_id, created_at__gte=one_month_ago)
            else:
                properties = Property.objects.filter(created_at__gte=one_month_ago)

            if not properties.exists():
                if user_id:
                    raise ValueError("No latest properties found for this user.")
                else:
                    raise ValueError("No latest properties found.")

            serializer = PropertySerializer(properties, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PropertiesByUserID(APIView):
    def get(self, request, user_id):
        try:
            properties = Property.objects.filter(user_id=user_id)
            serializer = PropertySerializer(properties, many=True)  # <-- FIXED HERE
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# class PropertiesByApprovalStatus(APIView):
#     def get(self, request, approval_status):
#         try:
#             properties = Property.objects.filter(approval_status=approval_status)
#             serializer = PropertySerializer(properties, many=True)  # <-- FIXED HERE
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PropertiesByApprovalStatus(APIView):
    def get(self, request, approval_status):
        try:
            properties = Property.objects.filter(approval_status=approval_status)
            response_data = []

            for prop in properties:
                # Serialize the property
                prop_data = PropertySerializer(prop).data
                buyer_data = None

                try:
                    # Prefer 'purchased' status first, fallback to 'booked'
                    user_property = (
                        prop.user_properties.filter(status='purchased').first()
                        or prop.user_properties.filter(status='booked').first()
                    )

                    if user_property:
                        user_info = UserSerializer(user_property.user).data
                        buyer_data = {
                            **user_info,
                            "booking_date": user_property.booking_date,
                            "purchase_date": user_property.purchase_date
                        }
                except UserProperty.DoesNotExist:
                    buyer_data = None

                # Add buyer_user to property data
                prop_data["buyer_user"] = buyer_data
                response_data.append(prop_data)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class PropertiesByStatus(APIView):
#     def get(self, request, property_status):
#         try:
#             properties = Property.objects.filter(status=property_status)
#             serializer = PropertySerializer(properties, many=True)  # <-- FIXED HERE
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class PropertiesByStatus(APIView):
    def get(self, request, property_status):
        try:
            properties = Property.objects.filter(status=property_status)
            response_data = []

            for prop in properties:
                # Serialize the property
                prop_data = PropertySerializer(prop).data
                buyer_data = None

                try:
                    # Prefer 'purchased' status first, fallback to 'booked'
                    user_property = (
                        prop.user_properties.filter(status='purchased').first()
                        or prop.user_properties.filter(status='booked').first()
                    )

                    if user_property:
                        user_info = UserSerializer(user_property.user).data
                        buyer_data = {
                            **user_info,
                            "booking_date": user_property.booking_date,
                            "purchase_date": user_property.purchase_date
                        }
                except UserProperty.DoesNotExist:
                    buyer_data = None

                # Add buyer_user to property data
                prop_data["buyer_user"] = buyer_data
                response_data.append(prop_data)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




#Working with Counts

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import Property, PropertyCategory, PropertyType

class PropertyStatsAPIView(APIView):
    def get(self, request):
        data = {}
        one_month_ago = timezone.now() - timedelta(days=30)

        # --- Category-wise Stats ---
        categories = PropertyCategory.objects.all()
        for category in categories:
            listing_qs = Property.objects.filter(category=category)
            latest_qs = listing_qs.filter(created_at__gte=one_month_ago)

            data[category.name] = {
                "listing_count": listing_qs.count(),
                "latest_count": latest_qs.count(),
                "sold": listing_qs.filter(status="sold").count(),
                "booked": listing_qs.filter(status="booked").count(),
                "available": listing_qs.filter(status="available").count(),
                "pending": listing_qs.filter(approval_status="pending").count(),
                "approved": listing_qs.filter(approval_status="approved").count(),
                "rejected": listing_qs.filter(approval_status="rejected").count(),
            }

        # --- Type-wise Stats ---
        types = PropertyType.objects.all()
        for prop_type in types:
            listing_qs = Property.objects.filter(property_type=prop_type)
            latest_qs = listing_qs.filter(created_at__gte=one_month_ago)

            data[prop_type.name] = {
                "listing_count": listing_qs.count(),
                "latest_count": latest_qs.count(),
                "sold": listing_qs.filter(status="sold").count(),
                "booked": listing_qs.filter(status="booked").count(),
                "available": listing_qs.filter(status="available").count(),
                "pending": listing_qs.filter(approval_status="pending").count(),
                "approved": listing_qs.filter(approval_status="approved").count(),
                "rejected": listing_qs.filter(approval_status="rejected").count(),
            }

        # --- Global Stats ---
        # for status_value in ['sold', 'booked', 'available']:
        #     data[status_value] = {
        #         "count": Property.objects.filter(status=status_value).count()
        #     }

        # for approval_value in ['pending', 'approved', 'rejected']:
        #     data[approval_value] = {
        #         "count": Property.objects.filter(approval_status=approval_value).count()
        #     }

        return Response(data, status=status.HTTP_200_OK)


#working with the property listing
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.utils import timezone
# from datetime import timedelta
# from .models import Property, PropertyCategory, PropertyType
# from .serializers import PropertySerializer

# class PropertyStatsAPIView(APIView):
#     def get(self, request):
#         data = {}
#         one_month_ago = timezone.now() - timedelta(days=30)

#         # --- Category-wise Stats ---
#         categories = PropertyCategory.objects.all()
#         for category in categories:
#             listing_qs = Property.objects.filter(category=category)
#             latest_qs = listing_qs.filter(created_at__gte=one_month_ago)

#             data[category.name] = {
#                 "listing_count": listing_qs.count(),
#                 "latest_count": latest_qs.count(),
#                 "sold": listing_qs.filter(status="sold").count(),
#                 "booked": listing_qs.filter(status="booked").count(),
#                 "available": listing_qs.filter(status="available").count(),
#                 "pending": listing_qs.filter(approval_status="pending").count(),
#                 "approved": listing_qs.filter(approval_status="approved").count(),
#                 "rejected": listing_qs.filter(approval_status="rejected").count(),
#                 "listing_properties": PropertySerializer(listing_qs, many=True).data,
#                 "latest_properties": PropertySerializer(latest_qs, many=True).data,
#             }

#         # --- Type-wise Stats ---
#         types = PropertyType.objects.all()
#         for prop_type in types:
#             listing_qs = Property.objects.filter(property_type=prop_type)
#             latest_qs = listing_qs.filter(created_at__gte=one_month_ago)

#             data[prop_type.name] = {
#                 "listing_count": listing_qs.count(),
#                 "latest_count": latest_qs.count(),
#                 "sold": listing_qs.filter(status="sold").count(),
#                 "booked": listing_qs.filter(status="booked").count(),
#                 "available": listing_qs.filter(status="available").count(),
#                 "pending": listing_qs.filter(approval_status="pending").count(),
#                 "approved": listing_qs.filter(approval_status="approved").count(),
#                 "rejected": listing_qs.filter(approval_status="rejected").count(),
#                 "listing_properties": PropertySerializer(listing_qs, many=True).data,
#                 "latest_properties": PropertySerializer(latest_qs, many=True).data,
#             }

#         # --- Global Status Counts and Lists ---
#         for status_value in ['sold', 'booked', 'available']:
#             status_qs = Property.objects.filter(status=status_value)
#             data[status_value] = {
#                 "count": status_qs.count(),
#                 "properties": PropertySerializer(status_qs, many=True).data
#             }

#         # --- Global Approval Status Counts and Lists ---
#         for approval_value in ['pending', 'approved', 'rejected']:
#             approval_qs = Property.objects.filter(approval_status=approval_value)
#             data[approval_value] = {
#                 "count": approval_qs.count(),
#                 "properties": PropertySerializer(approval_qs, many=True).data
#             }

#         return Response(data, status=status.HTTP_200_OK)




class PropertyStatsByUserAPIView_old(APIView):
    def get(self, request, user_id):
        data = {}
        one_month_ago = timezone.now() - timedelta(days=30)

        # Filter properties by user
        user_properties = Property.objects.filter(user_id=user_id)

        # Total listings
        #data["listing"] = user_properties.count()

        data["listing"] = {
            "properties": {
                "count": user_properties.count(),
                "list": PropertySerializer(user_properties, many=True).data
            }
        }



        # Latest listings in the last 30 days
        latest_qs = user_properties.filter(created_at__gte=one_month_ago)
        data["latest"] = {
            "properties": {
                "count": latest_qs.count(),
                "list": PropertySerializer(latest_qs, many=True).data
            }
        }

        # Status-wise data
        for status_value in ['sold', 'booked', 'available']:
            qs = user_properties.filter(status=status_value)
            data[status_value] = {
                "properties": {
                    "count": qs.count(),
                    "list": PropertySerializer(qs, many=True).data
                }
            }

        # Approval status-wise data
        for approval_status_value in ['pending', 'approved', 'rejected']:
            qs = user_properties.filter(approval_status=approval_status_value)
            data[approval_status_value] = {
                "properties": {
                    "count": qs.count(),
                    "list": PropertySerializer(qs, many=True).data
                }
            }

        return Response(data, status=status.HTTP_200_OK)


from users.serializers import *
from transactions.models import *
from users.models import *
from users.serializers import *


class PropertyStatsByUserAPIView_old2(APIView):
    def get(self, request, user_id):
        data = {}
        one_month_ago = timezone.now() - timedelta(days=30)

        # All properties listed by the user
        user_properties = Property.objects.filter(user_id=user_id)

        # Total listings
        data["listing"] = {
            "properties": {
                "count": user_properties.count(),
                "list": PropertySerializer(user_properties, many=True).data
            }
        }

        # Latest listings (last 30 days)
        latest_qs = user_properties.filter(created_at__gte=one_month_ago)
        data["latest"] = {
            "properties": {
                "count": latest_qs.count(),
                "list": PropertySerializer(latest_qs, many=True).data
            }
        }

        # Property status-wise data with buyer details
        for status_value in ['sold', 'booked', 'available']:
            qs = user_properties.filter(status=status_value)
            serialized_props = []

            for prop in qs:
                prop_data = PropertySerializer(prop).data
                if status_value in ['sold', 'booked']:
                    user_prop_status = 'purchased' if status_value == 'sold' else 'booked'
                    try:
                        user_property = UserProperty.objects.get(property=prop, status=user_prop_status)
                        buyer_data = UserSerializer(user_property.user).data
                    except UserProperty.DoesNotExist:
                        buyer_data = None
                    prop_data["buyer_user"] = buyer_data
                serialized_props.append(prop_data)

            data[status_value] = {
                "properties": {
                    "count": qs.count(),
                    "list": serialized_props
                }
            }

        # Approval status-wise data
        for approval_status_value in ['pending', 'approved', 'rejected']:
            qs = user_properties.filter(approval_status=approval_status_value)
            data[approval_status_value] = {
                "properties": {
                    "count": qs.count(),
                    "list": PropertySerializer(qs, many=True).data
                }
            }

        return Response(data, status=status.HTTP_200_OK)


class PropertyStatsByUserAPIView(APIView):
    def get(self, request, user_id):
        data = {}
        one_month_ago = timezone.now() - timedelta(days=30)

        # All properties listed by the user
        user_properties = Property.objects.filter(user_id=user_id)

        # Total listings
        data["listing"] = {
            "properties": {
                "count": user_properties.count(),
                "list": PropertySerializer(user_properties, many=True).data
            }
        }

        # Latest listings (last 30 days)
        latest_qs = user_properties.filter(created_at__gte=one_month_ago)
        data["latest"] = {
            "properties": {
                "count": latest_qs.count(),
                "list": PropertySerializer(latest_qs, many=True).data
            }
        }

        # Property status-wise data with buyer details
        for status_value in ['sold', 'booked', 'available']:
            qs = user_properties.filter(status=status_value)
            serialized_props = []

            for prop in qs:
                prop_data = PropertySerializer(prop).data
                buyer_data = None

                if status_value in ['sold', 'booked']:
                    user_prop_status = 'purchased' if status_value == 'sold' else 'booked'
                    try:
                        user_property = UserProperty.objects.get(property=prop, status=user_prop_status)
                        user_info = UserSerializer(user_property.user).data
                        buyer_data = {
                            **user_info,
                            "booking_date": user_property.booking_date,
                            "purchase_date": user_property.purchase_date
                        }
                    except UserProperty.DoesNotExist:
                        buyer_data = None

                prop_data["buyer_user"] = buyer_data
                serialized_props.append(prop_data)

            data[status_value] = {
                "properties": {
                    "count": qs.count(),
                    "list": serialized_props
                }
            }

        # Approval status-wise data
        for approval_status_value in ['pending', 'approved', 'rejected']:
            qs = user_properties.filter(approval_status=approval_status_value)
            data[approval_status_value] = {
                "properties": {
                    "count": qs.count(),
                    "list": PropertySerializer(qs, many=True).data
                }
            }

        return Response(data, status=status.HTTP_200_OK)





# ------------------ Amenity Views ------------------

class AmenityListCreateView(APIView):
    def get(self, request):
        try:
            amenities = Amenity.objects.all()
            serializer = AmenitySerializer(amenities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = AmenitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AmenityDetailView(APIView):
    def get_object(self, amenity_id):
        return get_object_or_404(Amenity, amenity_id=amenity_id)

    def get(self, request, amenity_id):
        try:
            amenity = self.get_object(amenity_id)
            serializer = AmenitySerializer(amenity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, amenity_id):
        try:
            amenity = self.get_object(amenity_id)
            serializer = AmenitySerializer(amenity, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, amenity_id):
        try:
            amenity = self.get_object(amenity_id)
            amenity.delete()
            return Response({"message": "Amenity deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





#EMI 


class EMIOptionListCreateAPIView(APIView):
    def get(self, request):
        options = EMIOption.objects.all()
        serializer = EMIOptionSerializer(options, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EMIOptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # emi_amount auto-calculated
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EMIOptionDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(EMIOption, pk=pk)

    def get(self, request, pk):
        emi_option = self.get_object(pk)
        serializer = EMIOptionSerializer(emi_option)
        return Response(serializer.data)

    def put(self, request, pk):
        emi_option = self.get_object(pk)
        serializer = EMIOptionSerializer(emi_option, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()  # Recalculate emi_amount
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        emi_option = self.get_object(pk)
        emi_option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)







class UserEMIListCreateAPIView(APIView):
    def get(self, request):
        emis = UserEMI.objects.all()
        serializer = UserEMISerializer(emis, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserEMISerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # end_date auto-calculated
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEMIDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(UserEMI, pk=pk)

    def get(self, request, pk):
        user_emi = self.get_object(pk)
        serializer = UserEMISerializer(user_emi)
        return Response(serializer.data)

    def put(self, request, pk):
        user_emi = self.get_object(pk)
        serializer = UserEMISerializer(user_emi, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()  # end_date recalculated
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_emi = self.get_object(pk)
        user_emi.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)







class BookingAmountSlabListCreateAPIView(APIView):
    def get(self, request):
        slabs = BookingAmountSlab.objects.all()
        serializer = BookingAmountSlabSerializer(slabs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingAmountSlabSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingAmountSlabDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(BookingAmountSlab, pk=pk)

    def get(self, request, pk):
        slab = self.get_object(pk)
        serializer = BookingAmountSlabSerializer(slab)
        return Response(serializer.data)

    def put(self, request, pk):
        slab = self.get_object(pk)
        serializer = BookingAmountSlabSerializer(slab, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        slab = self.get_object(pk)
        slab.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

















