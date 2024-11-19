from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, UserSerializer, ContactSerializer, SpamReportSerializer
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Contact, SpamReport, GlobalDatabase
from django.db.models import Count, Q


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Hello World!"}, status=status.HTTP_200_OK)


class ContactView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        phone_number = request.data.get('phone_number', '')
        if not phone_number.isdigit():
            return Response({'detail': 'Phone number must be a digit'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ContactSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            try:
                contact = serializer.save()
                return Response(ContactSerializer(contact).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpamReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SpamReportSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchByNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, name):
        try:
            starts_with_query = CustomUser.objects.filter(name__istartswith=name)
            contact_starts_with_query = Contact.objects.filter(name__istartswith=name, user=request.user)

            # Search for users whose name contains the search string but doesn't start with it
            contains_query = CustomUser.objects.filter(
                Q(name__icontains=name) & ~Q(name__istartswith=name)
            )

            # Search for contacts whose name contains the search string but doesn't start with it
            contact_contains_query = Contact.objects.filter(
                Q(name__icontains=name) & ~Q(name__istartswith=name), user=request.user
            )

            # Combine results from both queries
            results = list(starts_with_query) + list(contact_starts_with_query) + \
                     list(contains_query) + list(contact_contains_query)

            # Prepare the response data
            response_data = []
            for result in results:
                if isinstance(result, CustomUser):
                    spam_reports_count = SpamReport.objects.filter(phone_number=result.phone_number).count()
                    response_data.append({
                        "name": result.name,
                        "phone_number": result.phone_number,
                        "spam_reports_count": spam_reports_count
                    })
                elif isinstance(result, Contact):
                    spam_reports_count = SpamReport.objects.filter(phone_number=result.phone_number).count()
                    response_data.append({
                        "name": result.name,
                        "phone_number": result.phone_number,
                        "spam_reports_count": spam_reports_count
                    })

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SearchByPhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, phone_number):
        try:
            response_data = []
            registered_user = CustomUser.objects.filter(phone_number=phone_number).first()
            if registered_user:
                is_in_contact_list = Contact.objects.filter(user=request.user, phone_number=phone_number).exists()

                if is_in_contact_list:
                    response_data.append({
                        "name": registered_user.name,
                        "phone_number": registered_user.phone_number,
                        "email": registered_user.email,
                        "spam_reports_count": SpamReport.objects.filter(phone_number=phone_number).count(),
                    })
                else:
                    response_data.append({
                        "name": registered_user.name,
                        "phone_number": registered_user.phone_number,
                        "spam_reports_count": SpamReport.objects.filter(phone_number=phone_number).count(),
                    })

            else:
                contact = Contact.objects.filter(user=request.user, phone_number=phone_number).first()

                if contact:
                    response_data.append({
                        "name": contact.name,
                        "phone_number": contact.phone_number,
                        "email": contact.user.email,
                        "spam_reports_count": SpamReport.objects.filter(phone_number=phone_number).count(),
                    })
                else:
                    response_data.append({
                        "name": contact.name,
                        "phone_number": contact.phone_number,
                        "spam_reports_count": SpamReport.objects.filter(phone_number=phone_number).count(),
                    })

            if not response_data:
                return Response({"detail": "No results found."}, status=status.HTTP_404_NOT_FOUND)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
